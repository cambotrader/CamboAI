from sqlalchemy.orm import Session
from app.database import User, Portfolio, Position, Transaction, PerformanceRecord, BrokerAPIKey, Alert, RiskMetric
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import uuid

class UserService:
    @staticmethod
    def create_user(db: Session, email: str, password: str, first_name: str = None, last_name: str = None) -> User:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

class PortfolioService:
    @staticmethod
    def create_portfolio(db: Session, user_id: uuid.UUID, name: str, description: str = None, initial_value: float = 0.0) -> Portfolio:
        db_portfolio = Portfolio(
            user_id=user_id,
            name=name,
            description=description,
            initial_value=initial_value,
            current_value=initial_value,
            cash_balance=initial_value
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    
    @staticmethod
    def get_user_portfolios(db: Session, user_id: uuid.UUID) -> List[Portfolio]:
        return db.query(Portfolio).filter(Portfolio.user_id == user_id, Portfolio.is_active == True).all()
    
    @staticmethod
    def get_portfolio_by_id(db: Session, portfolio_id: uuid.UUID) -> Optional[Portfolio]:
        return db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    
    @staticmethod
    def update_portfolio_value(db: Session, portfolio_id: uuid.UUID, new_value: float):
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            portfolio.current_value = new_value
            portfolio.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(portfolio)
        return portfolio

class PositionService:
    @staticmethod
    def create_position(db: Session, portfolio_id: uuid.UUID, symbol: str, quantity: float, average_cost: float) -> Position:
        db_position = Position(
            portfolio_id=portfolio_id,
            symbol=symbol,
            quantity=quantity,
            average_cost=average_cost,
            market_value=quantity * average_cost
        )
        db.add(db_position)
        db.commit()
        db.refresh(db_position)
        return db_position
    
    @staticmethod
    def get_portfolio_positions(db: Session, portfolio_id: uuid.UUID) -> List[Position]:
        return db.query(Position).filter(
            Position.portfolio_id == portfolio_id, 
            Position.is_active == True,
            Position.quantity != 0
        ).all()
    
    @staticmethod
    def update_position_price(db: Session, position_id: uuid.UUID, current_price: float):
        position = db.query(Position).filter(Position.id == position_id).first()
        if position:
            position.current_price = current_price
            position.market_value = position.quantity * current_price
            position.unrealized_pnl = position.market_value - (position.quantity * position.average_cost)
            position.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(position)
        return position
    
    @staticmethod
    def update_position_quantity(db: Session, portfolio_id: uuid.UUID, symbol: str, quantity_change: float, price: float, transaction_type: str):
        """Update position quantity based on a transaction"""
        position = db.query(Position).filter(
            Position.portfolio_id == portfolio_id,
            Position.symbol == symbol,
            Position.is_active == True
        ).first()
        
        if not position and quantity_change > 0:
            # Create new position
            return PositionService.create_position(db, portfolio_id, symbol, quantity_change, price)
        
        elif position:
            if transaction_type == "BUY":
                # Update average cost with new shares
                total_cost = (position.quantity * position.average_cost) + (quantity_change * price)
                new_quantity = position.quantity + quantity_change
                position.average_cost = total_cost / new_quantity if new_quantity > 0 else 0
                position.quantity = new_quantity
            elif transaction_type == "SELL":
                position.quantity -= quantity_change
                if position.quantity <= 0:
                    position.is_active = False
                    position.quantity = 0
            
            position.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(position)
        
        return position

class TransactionService:
    @staticmethod
    def create_transaction(db: Session, portfolio_id: uuid.UUID, symbol: str, transaction_type: str, 
                          quantity: float, price: float, fees: float = 0.0, broker_order_id: str = None) -> Transaction:
        total_amount = quantity * price + fees
        
        db_transaction = Transaction(
            portfolio_id=portfolio_id,
            symbol=symbol,
            transaction_type=transaction_type,
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            fees=fees,
            broker_order_id=broker_order_id
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        # Update position
        PositionService.update_position_quantity(db, portfolio_id, symbol, quantity, price, transaction_type)
        
        return db_transaction
    
    @staticmethod
    def get_portfolio_transactions(db: Session, portfolio_id: uuid.UUID, limit: int = 100) -> List[Transaction]:
        return db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio_id
        ).order_by(Transaction.executed_at.desc()).limit(limit).all()

class PerformanceService:
    @staticmethod
    def create_performance_record(db: Session, portfolio_id: uuid.UUID, date: datetime, 
                                 total_value: float, cash_value: float, positions_value: float) -> PerformanceRecord:
        # Calculate returns
        previous_record = db.query(PerformanceRecord).filter(
            PerformanceRecord.portfolio_id == portfolio_id,
            PerformanceRecord.date < date
        ).order_by(PerformanceRecord.date.desc()).first()
        
        daily_return = 0.0
        cumulative_return = 0.0
        
        if previous_record:
            daily_return = (total_value - previous_record.total_value) / previous_record.total_value
            
            portfolio = PortfolioService.get_portfolio_by_id(db, portfolio_id)
            if portfolio and portfolio.initial_value > 0:
                cumulative_return = (total_value - portfolio.initial_value) / portfolio.initial_value
        
        db_performance = PerformanceRecord(
            portfolio_id=portfolio_id,
            date=date,
            total_value=total_value,
            cash_value=cash_value,
            positions_value=positions_value,
            daily_return=daily_return,
            cumulative_return=cumulative_return
        )
        db.add(db_performance)
        db.commit()
        db.refresh(db_performance)
        return db_performance
    
    @staticmethod
    def get_portfolio_performance(db: Session, portfolio_id: uuid.UUID, days: int = 30) -> List[PerformanceRecord]:
        start_date = datetime.utcnow() - timedelta(days=days)
        return db.query(PerformanceRecord).filter(
            PerformanceRecord.portfolio_id == portfolio_id,
            PerformanceRecord.date >= start_date
        ).order_by(PerformanceRecord.date.asc()).all()

class BrokerService:
    @staticmethod
    def create_api_key(db: Session, user_id: uuid.UUID, broker_name: str, api_key: str, 
                      api_secret: str, base_url: str = None, is_paper_trading: bool = True) -> BrokerAPIKey:
        db_api_key = BrokerAPIKey(
            user_id=user_id,
            broker_name=broker_name,
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            is_paper_trading=is_paper_trading
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        return db_api_key
    
    @staticmethod
    def get_user_broker_keys(db: Session, user_id: uuid.UUID) -> List[BrokerAPIKey]:
        return db.query(BrokerAPIKey).filter(
            BrokerAPIKey.user_id == user_id,
            BrokerAPIKey.is_active == True
        ).all()

class AlertService:
    @staticmethod
    def create_alert(db: Session, user_id: uuid.UUID, alert_type: str, condition: str, 
                    threshold_value: float = None, symbol: str = None, message: str = None) -> Alert:
        db_alert = Alert(
            user_id=user_id,
            alert_type=alert_type,
            symbol=symbol,
            condition=condition,
            threshold_value=threshold_value,
            message=message
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return db_alert
    
    @staticmethod
    def get_user_alerts(db: Session, user_id: uuid.UUID, active_only: bool = True) -> List[Alert]:
        query = db.query(Alert).filter(Alert.user_id == user_id)
        if active_only:
            query = query.filter(Alert.is_active == True)
        return query.all()
    
    @staticmethod
    def trigger_alert(db: Session, alert_id: uuid.UUID, message: str = None):
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.is_triggered = True
            alert.triggered_at = datetime.utcnow()
            if message:
                alert.message = message
            db.commit()
            db.refresh(alert)
        return alert

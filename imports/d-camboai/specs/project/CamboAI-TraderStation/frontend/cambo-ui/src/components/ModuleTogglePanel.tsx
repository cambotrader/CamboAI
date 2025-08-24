import React, { useState, useEffect } from 'react';
import './ModuleTogglePanel.css';

interface Module {
  name: string;
  enabled: boolean;
  depends_on: string[];
  webhook_url: string;
  file_exists: boolean;
  last_modified: string | null;
}

interface ValidationResult {
  success: boolean;
  output: string;
  timestamp: string;
}

interface ToggleHistory {
  module: string;
  history: string[];
}

const ModuleTogglePanel: React.FC = () => {
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [selectedModule, setSelectedModule] = useState<string | null>(null);
  const [moduleHistory, setModuleHistory] = useState<ToggleHistory | null>(null);
  const [showHistory, setShowHistory] = useState(false);

  const API_BASE = 'http://localhost:8080/api';

  useEffect(() => {
    fetchModules();
  }, []);

  const fetchModules = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/modules`);
      if (!response.ok) throw new Error('Failed to fetch modules');
      const data = await response.json();
      setModules(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const toggleModule = async (moduleName: string) => {
    try {
      const response = await fetch(`${API_BASE}/modules/${moduleName}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ source: 'React UI' }),
      });

      if (!response.ok) throw new Error('Failed to toggle module');
      
      const result = await response.json();
      
      // Update local state
      setModules(prev => 
        prev.map(module => 
          module.name === moduleName 
            ? { ...module, enabled: result.enabled }
            : module
        )
      );

      // Show success message
      console.log(result.message);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle module');
    }
  };

  const validateModules = async () => {
    try {
      const response = await fetch(`${API_BASE}/validate`);
      if (!response.ok) throw new Error('Failed to validate modules');
      const data = await response.json();
      setValidation(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Validation failed');
    }
  };

  const fetchModuleHistory = async (moduleName: string) => {
    try {
      const response = await fetch(`${API_BASE}/modules/${moduleName}/history`);
      if (!response.ok) throw new Error('Failed to fetch history');
      const data = await response.json();
      setModuleHistory(data);
      setSelectedModule(moduleName);
      setShowHistory(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch history');
    }
  };

  const getDependencyStatus = (module: Module): 'valid' | 'warning' | 'error' => {
    if (!module.depends_on || module.depends_on.length === 0) return 'valid';
    
    for (const dep of module.depends_on) {
      const depModule = modules.find(m => m.name === dep);
      if (!depModule) return 'error';
      if (!depModule.enabled) return 'warning';
    }
    return 'valid';
  };

  const getModuleStatusIcon = (module: Module): string => {
    if (!module.file_exists) return '❌';
    if (!module.enabled) return '⭕';
    
    const depStatus = getDependencyStatus(module);
    if (depStatus === 'error') return '🚫';
    if (depStatus === 'warning') return '⚠️';
    
    return '✅';
  };

  const getModuleStatusText = (module: Module): string => {
    if (!module.file_exists) return 'File Missing';
    if (!module.enabled) return 'Disabled';
    
    const depStatus = getDependencyStatus(module);
    if (depStatus === 'error') return 'Missing Dependencies';
    if (depStatus === 'warning') return 'Dependencies Disabled';
    
    return 'Ready';
  };

  if (loading) {
    return (
      <div className="toggle-panel">
        <div className="loading">Loading modules...</div>
      </div>
    );
  }

  return (
    <div className="toggle-panel">
      <div className="panel-header">
        <h2>🔧 Cambo Module Controller</h2>
        <div className="panel-actions">
          <button onClick={fetchModules} className="btn btn-refresh">
            🔄 Refresh
          </button>
          <button onClick={validateModules} className="btn btn-validate">
            ✅ Validate
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          ❌ {error}
          <button onClick={() => setError(null)} className="close-btn">×</button>
        </div>
      )}

      <div className="modules-grid">
        {modules.map((module) => (
          <div key={module.name} className={`module-card ${module.enabled ? 'enabled' : 'disabled'}`}>
            <div className="module-header">
              <div className="module-info">
                <span className="module-icon">{getModuleStatusIcon(module)}</span>
                <div>
                  <h3 className="module-name">{module.name}</h3>
                  <span className="module-status">{getModuleStatusText(module)}</span>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={module.enabled}
                  onChange={() => toggleModule(module.name)}
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="module-details">
              {module.depends_on && module.depends_on.length > 0 && (
                <div className="dependencies">
                  <strong>Dependencies:</strong>
                  <div className="dep-list">
                    {module.depends_on.map((dep) => {
                      const depModule = modules.find(m => m.name === dep);
                      const depStatus = depModule ? (depModule.enabled ? 'enabled' : 'disabled') : 'missing';
                      return (
                        <span key={dep} className={`dep-tag ${depStatus}`}>
                          {dep}
                        </span>
                      );
                    })}
                  </div>
                </div>
              )}

              {module.last_modified && (
                <div className="last-modified">
                  <strong>Modified:</strong> {module.last_modified}
                </div>
              )}

              <div className="module-actions">
                <button 
                  onClick={() => fetchModuleHistory(module.name)}
                  className="btn btn-small btn-history"
                >
                  📊 History
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {validation && (
        <div className="validation-panel">
          <h3>🔍 Validation Results</h3>
          <div className={`validation-status ${validation.success ? 'success' : 'error'}`}>
            {validation.success ? '✅ All checks passed' : '❌ Issues found'}
          </div>
          <pre className="validation-output">{validation.output}</pre>
          <div className="validation-timestamp">
            Last validated: {validation.timestamp}
          </div>
        </div>
      )}

      {showHistory && moduleHistory && (
        <div className="history-modal">
          <div className="history-content">
            <div className="history-header">
              <h3>📊 Toggle History: {moduleHistory.module}</h3>
              <button onClick={() => setShowHistory(false)} className="close-btn">×</button>
            </div>
            <div className="history-list">
              {moduleHistory.history.length > 0 ? (
                moduleHistory.history.map((entry, index) => (
                  <div key={index} className="history-entry">
                    {entry}
                  </div>
                ))
              ) : (
                <div className="no-history">No toggle history found</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModuleTogglePanel;
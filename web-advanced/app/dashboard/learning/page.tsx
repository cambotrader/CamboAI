"use client";
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

type Course = {
  id: string;
  title: string;
  description: string;
  hero_image?: string;
  published: boolean;
  modules_count: number;
  lessons_count: number;
  duration_hours: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  progress: number;
};

type Lesson = {
  id: string;
  title: string;
  type: 'video' | 'article' | 'quiz' | 'assignment';
  duration_sec: number;
  completed: boolean;
  content_preview: string;
};

type Quiz = {
  id: string;
  title: string;
  questions_count: number;
  passing_score: number;
  your_score?: number;
  attempts: number;
  time_limit_minutes: number;
};

export default function LearningPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('courses');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    // Mock courses data - replace with real API call to /api/learning/courses
    const mockCourses: Course[] = [
      {
        id: '1',
        title: 'Options Trading Fundamentals',
        description: 'Master the basics of options trading, from calls and puts to complex strategies',
        published: true,
        modules_count: 6,
        lessons_count: 24,
        duration_hours: 8,
        difficulty: 'beginner',
        progress: 65
      },
      {
        id: '2',
        title: 'Technical Analysis Deep Dive',
        description: 'Advanced chart patterns, indicators, and trading signals for professional traders',
        published: true,
        modules_count: 8,
        lessons_count: 32,
        duration_hours: 12,
        difficulty: 'intermediate',
        progress: 30
      },
      {
        id: '3',
        title: 'Risk Management & Portfolio Theory',
        description: 'Learn how to protect your capital and optimize portfolio construction',
        published: true,
        modules_count: 5,
        lessons_count: 18,
        duration_hours: 6,
        difficulty: 'advanced',
        progress: 0
      },
      {
        id: '4',
        title: 'Algorithmic Trading with Python',
        description: 'Build automated trading systems using Python, APIs, and quantitative strategies',
        published: true,
        modules_count: 10,
        lessons_count: 45,
        duration_hours: 20,
        difficulty: 'advanced',
        progress: 15
      },
      {
        id: '5',
        title: 'Market Psychology & Sentiment',
        description: 'Understanding crowd behavior, fear/greed cycles, and behavioral finance',
        published: true,
        modules_count: 4,
        lessons_count: 16,
        duration_hours: 5,
        difficulty: 'intermediate',
        progress: 80
      }
    ];
    setCourses(mockCourses);
  };

  const loadCourseDetails = async (course: Course) => {
    setLoading(true);
    setSelectedCourse(course);
    
    // Mock lessons and quizzes - replace with real API calls
    const mockLessons: Lesson[] = [
      {
        id: '1',
        title: 'What are Options?',
        type: 'video',
        duration_sec: 480,
        completed: true,
        content_preview: 'Introduction to options contracts, calls vs puts, and basic terminology...'
      },
      {
        id: '2',
        title: 'Options Pricing Fundamentals',
        type: 'article',
        duration_sec: 600,
        completed: true,
        content_preview: 'Learn about intrinsic vs extrinsic value, time decay, and the Greeks...'
      },
      {
        id: '3',
        title: 'Basic Options Strategies',
        type: 'video',
        duration_sec: 720,
        completed: false,
        content_preview: 'Covered calls, protective puts, and simple spread strategies...'
      },
      {
        id: '4',
        title: 'Risk Assessment Quiz',
        type: 'quiz',
        duration_sec: 900,
        completed: false,
        content_preview: 'Test your understanding of options risk and reward profiles...'
      }
    ];
    
    const mockQuizzes: Quiz[] = [
      {
        id: '1',
        title: 'Options Fundamentals Quiz',
        questions_count: 10,
        passing_score: 80,
        your_score: 90,
        attempts: 1,
        time_limit_minutes: 15
      },
      {
        id: '2',
        title: 'Greeks & Pricing Quiz',
        questions_count: 15,
        passing_score: 75,
        attempts: 0,
        time_limit_minutes: 20
      }
    ];
    
    setLessons(mockLessons);
    setQuizzes(mockQuizzes);
    setLoading(false);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getLessonIcon = (type: string) => {
    switch (type) {
      case 'video': return '🎥';
      case 'article': return '📄';
      case 'quiz': return '❓';
      case 'assignment': return '📝';
      default: return '📚';
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    return minutes < 60 ? `${minutes}m` : `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">🎓 Learning Center</h1>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            📊 My Progress
          </Button>
          <Button variant="outline" size="sm">
            🏆 Certificates
          </Button>
          <Button size="sm">
            + Browse Courses
          </Button>
        </div>
      </div>

      {!selectedCourse ? (
        // Course Catalog View
        <>
          {/* Learning Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Courses Enrolled</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">5</div>
                <p className="text-xs text-gray-500">3 in progress</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Hours Completed</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">28.5</div>
                <p className="text-xs text-gray-500">This month</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Certificates</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">2</div>
                <p className="text-xs text-gray-500">Options + TA</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm text-gray-600">Quiz Average</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">87%</div>
                <p className="text-xs text-gray-500">12 quizzes</p>
              </CardContent>
            </Card>
          </div>

          {/* Course Grid */}
          <Card>
            <CardHeader>
              <CardTitle>📚 My Courses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courses.map((course) => (
                  <Card key={course.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg mb-2">{course.title}</h3>
                            <p className="text-sm text-gray-600 mb-3">{course.description}</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Badge className={getDifficultyColor(course.difficulty)}>
                            {course.difficulty}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {course.lessons_count} lessons • {course.duration_hours}h
                          </span>
                        </div>
                        
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Progress</span>
                            <span>{course.progress}%</span>
                          </div>
                          <Progress value={course.progress} />
                        </div>
                        
                        <Button 
                          className="w-full"
                          onClick={() => loadCourseDetails(course)}
                          disabled={loading}
                        >
                          {course.progress === 0 ? 'Start Course' : 'Continue Learning'}
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        // Course Detail View
        <div className="space-y-6">
          {/* Course Header */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
            <CardContent className="pt-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <Button variant="ghost" size="sm" onClick={() => setSelectedCourse(null)}>
                      ← Back to Courses
                    </Button>
                    <Badge className={getDifficultyColor(selectedCourse.difficulty)}>
                      {selectedCourse.difficulty}
                    </Badge>
                  </div>
                  <h1 className="text-3xl font-bold mb-2">{selectedCourse.title}</h1>
                  <p className="text-gray-600 mb-4">{selectedCourse.description}</p>
                  
                  <div className="flex items-center space-x-6 text-sm text-gray-500">
                    <span>📚 {selectedCourse.lessons_count} lessons</span>
                    <span>⏱️ {selectedCourse.duration_hours} hours</span>
                    <span>📊 {selectedCourse.progress}% complete</span>
                  </div>
                </div>
                
                <div className="w-32">
                  <div className="text-center mb-2">
                    <div className="text-3xl font-bold text-blue-600">{selectedCourse.progress}%</div>
                    <div className="text-sm text-gray-500">Complete</div>
                  </div>
                  <Progress value={selectedCourse.progress} />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Course Content */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList>
              <TabsTrigger value="lessons">Lessons</TabsTrigger>
              <TabsTrigger value="quizzes">Quizzes</TabsTrigger>
              <TabsTrigger value="resources">Resources</TabsTrigger>
              <TabsTrigger value="discussion">Discussion</TabsTrigger>
            </TabsList>
            
            <TabsContent value="lessons" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>📖 Course Lessons</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {lessons.map((lesson, index) => (
                      <div key={lesson.id} className={`p-4 border rounded-lg ${
                        lesson.completed ? 'bg-green-50 border-green-200' : 'bg-gray-50'
                      }`}>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                              <span className="text-2xl">{getLessonIcon(lesson.type)}</span>
                              {lesson.completed && <span className="text-green-600">✅</span>}
                            </div>
                            <div className="flex-1">
                              <div className="font-semibold">{lesson.title}</div>
                              <div className="text-sm text-gray-600 mt-1">
                                {lesson.content_preview}
                              </div>
                              <div className="text-xs text-gray-500 mt-2">
                                {lesson.type.toUpperCase()} • {formatDuration(lesson.duration_sec)}
                              </div>
                            </div>
                          </div>
                          <Button 
                            size="sm"
                            variant={lesson.completed ? 'outline' : 'default'}
                          >
                            {lesson.completed ? 'Review' : 'Start'}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="quizzes" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>❓ Course Quizzes</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {quizzes.map((quiz) => (
                      <div key={quiz.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg">{quiz.title}</h3>
                            <div className="text-sm text-gray-600 mt-2">
                              {quiz.questions_count} questions • {quiz.time_limit_minutes} minutes • Passing: {quiz.passing_score}%
                            </div>
                            {quiz.your_score && (
                              <div className="mt-2">
                                <Badge className={quiz.your_score >= quiz.passing_score ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                                  Your Score: {quiz.your_score}%
                                </Badge>
                              </div>
                            )}
                          </div>
                          <div className="text-right">
                            <Button size="sm">
                              {quiz.attempts === 0 ? 'Take Quiz' : 'Retake'}
                            </Button>
                            <div className="text-xs text-gray-500 mt-1">
                              Attempts: {quiz.attempts}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="resources">
              <Card>
                <CardHeader>
                  <CardTitle>📎 Additional Resources</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {[
                      { name: 'Options Trading Cheat Sheet', type: 'PDF', size: '2.1 MB' },
                      { name: 'Greek Calculator Spreadsheet', type: 'Excel', size: '1.5 MB' },
                      { name: 'Strategy Comparison Chart', type: 'PDF', size: '800 KB' },
                      { name: 'Recommended Reading List', type: 'Document', size: '150 KB' }
                    ].map((resource, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">📄</span>
                          <div>
                            <div className="font-medium">{resource.name}</div>
                            <div className="text-sm text-gray-500">{resource.type} • {resource.size}</div>
                          </div>
                        </div>
                        <Button size="sm" variant="outline">Download</Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="discussion">
              <Card>
                <CardHeader>
                  <CardTitle>💬 Course Discussion</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    <span className="text-4xl block mb-2">💬</span>
                    Discussion feature coming soon!
                    <div className="text-sm mt-2">Connect with other learners and instructors</div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      )}
    </div>
  );
}
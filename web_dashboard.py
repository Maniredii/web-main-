#!/usr/bin/env python3
"""
🌐 LinkedIn Automation Web Dashboard
Real-time monitoring and control interface
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Import our automation modules
from linkedin_ollama_automation import LinkedInOllamaAutomation, AutomationStrategy
from advanced_job_analyzer import AdvancedJobAnalyzer

app = Flask(__name__)
app.secret_key = 'linkedin_automation_secret_key'

# Global state
automation_status = {
    'running': False,
    'start_time': None,
    'applications_sent': 0,
    'applications_failed': 0,
    'current_job': None,
    'last_activity': None,
    'errors': []
}

automation_instance = None
automation_thread = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardManager:
    """Manages dashboard state and automation control"""
    
    def __init__(self):
        self.config = self.load_config()
        self.job_analyzer = AdvancedJobAnalyzer()
        self.application_history = []
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from config.json"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to config.json"""
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_application_history(self) -> List[Dict[str, Any]]:
        """Get application history from log files"""
        history = []
        
        # Look for job application log files
        for filename in os.listdir('.'):
            if filename.startswith('job_applications_') and filename.endswith('.json'):
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            history.extend(data)
                        else:
                            history.append(data)
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
        
        # Sort by timestamp
        history.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return history[:50]  # Return last 50 applications
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get automation statistics"""
        history = self.get_application_history()
        
        total_applications = len(history)
        successful_applications = len([app for app in history if app.get('success', False)])
        failed_applications = total_applications - successful_applications
        
        # Calculate success rate
        success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_applications = [
            app for app in history 
            if datetime.fromtimestamp(app.get('timestamp', 0)) > yesterday
        ]
        
        return {
            'total_applications': total_applications,
            'successful_applications': successful_applications,
            'failed_applications': failed_applications,
            'success_rate': round(success_rate, 2),
            'recent_applications': len(recent_applications),
            'running_time': self.get_running_time(),
            'current_status': automation_status['running']
        }
    
    def get_running_time(self) -> str:
        """Get automation running time"""
        if not automation_status['start_time']:
            return "Not running"
        
        elapsed = datetime.now() - automation_status['start_time']
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def start_automation(self, strategy: str = "conservative") -> bool:
        """Start the automation in a separate thread"""
        global automation_instance, automation_thread, automation_status
        
        if automation_status['running']:
            return False
        
        try:
            # Create automation instance
            strategy_enum = AutomationStrategy.CONSERVATIVE
            if strategy == "adaptive":
                strategy_enum = AutomationStrategy.ADAPTIVE
            elif strategy == "aggressive":
                strategy_enum = AutomationStrategy.AGGRESSIVE
            
            automation_instance = LinkedInOllamaAutomation(
                profile_path="my_details.json",
                strategy=strategy_enum
            )
            
            # Update status
            automation_status['running'] = True
            automation_status['start_time'] = datetime.now()
            automation_status['applications_sent'] = 0
            automation_status['applications_failed'] = 0
            automation_status['errors'] = []
            
            # Start automation in separate thread
            automation_thread = threading.Thread(target=self._run_automation)
            automation_thread.daemon = True
            automation_thread.start()
            
            logger.info("Automation started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start automation: {e}")
            automation_status['errors'].append(str(e))
            return False
    
    def stop_automation(self) -> bool:
        """Stop the automation"""
        global automation_status
        
        if not automation_status['running']:
            return False
        
        try:
            automation_status['running'] = False
            automation_status['last_activity'] = datetime.now()
            
            if automation_instance:
                automation_instance._cleanup()
            
            logger.info("Automation stopped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop automation: {e}")
            return False
    
    def _run_automation(self):
        """Run automation in background thread"""
        global automation_status
        
        try:
            if automation_instance:
                automation_instance.run_automation()
        except Exception as e:
            logger.error(f"Automation error: {e}")
            automation_status['errors'].append(str(e))
        finally:
            automation_status['running'] = False
            automation_status['last_activity'] = datetime.now()

# Initialize dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def index():
    """Main dashboard page"""
    stats = dashboard_manager.get_statistics()
    config = dashboard_manager.config
    history = dashboard_manager.get_application_history()[:10]  # Recent 10 applications
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         config=config, 
                         history=history,
                         status=automation_status)

@app.route('/api/start', methods=['POST'])
def api_start_automation():
    """API endpoint to start automation"""
    data = request.get_json()
    strategy = data.get('strategy', 'conservative')
    
    success = dashboard_manager.start_automation(strategy)
    
    return jsonify({
        'success': success,
        'message': 'Automation started successfully' if success else 'Failed to start automation'
    })

@app.route('/api/stop', methods=['POST'])
def api_stop_automation():
    """API endpoint to stop automation"""
    success = dashboard_manager.stop_automation()
    
    return jsonify({
        'success': success,
        'message': 'Automation stopped successfully' if success else 'Failed to stop automation'
    })

@app.route('/api/status')
def api_status():
    """API endpoint to get current status"""
    stats = dashboard_manager.get_statistics()
    
    return jsonify({
        'status': automation_status,
        'statistics': stats
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """API endpoint to get/update configuration"""
    if request.method == 'POST':
        config = request.get_json()
        success = dashboard_manager.save_config(config)
        return jsonify({'success': success})
    else:
        return jsonify(dashboard_manager.config)

@app.route('/api/history')
def api_history():
    """API endpoint to get application history"""
    history = dashboard_manager.get_application_history()
    return jsonify(history)

@app.route('/api/analyze_job', methods=['POST'])
def api_analyze_job():
    """API endpoint to analyze a job"""
    data = request.get_json()
    job_data = data.get('job_data', {})
    user_profile = data.get('user_profile', {})
    
    try:
        analysis = dashboard_manager.job_analyzer.analyze_job_compatibility(job_data, user_profile)
        
        return jsonify({
            'success': True,
            'analysis': {
                'overall_score': analysis.overall_score,
                'compatibility_score': analysis.compatibility_score,
                'skill_match_score': analysis.skill_match_score,
                'should_apply': analysis.should_apply,
                'reasoning': analysis.reasoning,
                'skill_gaps': analysis.skill_gaps,
                'skill_matches': analysis.skill_matches,
                'application_strategy': analysis.application_strategy
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/generate_cover_letter', methods=['POST'])
def api_generate_cover_letter():
    """API endpoint to generate cover letter"""
    data = request.get_json()
    job_data = data.get('job_data', {})
    user_profile = data.get('user_profile', {})
    analysis_data = data.get('analysis', {})
    
    try:
        # Create analysis object
        from advanced_job_analyzer import JobAnalysis
        analysis = JobAnalysis(
            job_title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            overall_score=analysis_data.get('overall_score', 0.0),
            compatibility_score=analysis_data.get('compatibility_score', 0.0),
            skill_match_score=analysis_data.get('skill_match_score', 0.0),
            salary_score=analysis_data.get('salary_score', 0.0),
            culture_score=analysis_data.get('culture_score', 0.0),
            success_probability=analysis_data.get('success_probability', 0.0),
            should_apply=analysis_data.get('should_apply', False),
            reasoning=analysis_data.get('reasoning', ''),
            skill_gaps=analysis_data.get('skill_gaps', []),
            skill_matches=analysis_data.get('skill_matches', []),
            salary_insights=analysis_data.get('salary_insights', {}),
            company_insights=analysis_data.get('company_insights', {}),
            cover_letter_suggestions=analysis_data.get('cover_letter_suggestions', []),
            application_strategy=analysis_data.get('application_strategy', '')
        )
        
        cover_letter = dashboard_manager.job_analyzer.generate_cover_letter(job_data, user_profile, analysis)
        
        return jsonify({
            'success': True,
            'cover_letter': cover_letter
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the dashboard template
    create_dashboard_template()
    
    print("🌐 Starting LinkedIn Automation Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔒 Make sure Ollama is running for AI features")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_dashboard_template():
    """Create the dashboard HTML template"""
    template_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Automation Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <div>
                        <h1 class="text-3xl font-bold text-gray-900">LinkedIn Automation Dashboard</h1>
                        <p class="text-gray-600">Real-time monitoring and control</p>
                    </div>
                    <div class="flex space-x-4">
                        <button id="startBtn" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
                            Start Automation
                        </button>
                        <button id="stopBtn" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg" disabled>
                            Stop Automation
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Statistics Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-blue-100 text-blue-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Applications</p>
                            <p class="text-2xl font-semibold text-gray-900" id="totalApplications">0</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-green-100 text-green-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Success Rate</p>
                            <p class="text-2xl font-semibold text-gray-900" id="successRate">0%</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-yellow-100 text-yellow-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Running Time</p>
                            <p class="text-2xl font-semibold text-gray-900" id="runningTime">Not running</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-purple-100 text-purple-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Status</p>
                            <p class="text-2xl font-semibold text-gray-900" id="status">Stopped</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts and Tables -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Application History -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900">Recent Applications</h3>
                    </div>
                    <div class="p-6">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                                    </tr>
                                </thead>
                                <tbody id="applicationHistory" class="bg-white divide-y divide-gray-200">
                                    <!-- Application history will be populated here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Job Analysis -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900">Job Analysis</h3>
                    </div>
                    <div class="p-6">
                        <div id="jobAnalysisForm">
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Job Title</label>
                                    <input type="text" id="jobTitle" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Company</label>
                                    <input type="text" id="jobCompany" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Job Description</label>
                                    <textarea id="jobDescription" rows="4" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"></textarea>
                                </div>
                                <button id="analyzeJobBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                                    Analyze Job
                                </button>
                            </div>
                        </div>
                        <div id="analysisResults" class="mt-6 hidden">
                            <!-- Analysis results will be shown here -->
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Dashboard JavaScript
        let statusInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadStatus();
            loadApplicationHistory();
            setupEventListeners();
            
            // Update status every 5 seconds
            statusInterval = setInterval(loadStatus, 5000);
        });
        
        function setupEventListeners() {
            document.getElementById('startBtn').addEventListener('click', startAutomation);
            document.getElementById('stopBtn').addEventListener('click', stopAutomation);
            document.getElementById('analyzeJobBtn').addEventListener('click', analyzeJob);
        }
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateDashboard(data.statistics, data.status);
            } catch (error) {
                console.error('Failed to load status:', error);
            }
        }
        
        function updateDashboard(stats, status) {
            document.getElementById('totalApplications').textContent = stats.total_applications;
            document.getElementById('successRate').textContent = stats.success_rate + '%';
            document.getElementById('runningTime').textContent = stats.running_time;
            document.getElementById('status').textContent = status.running ? 'Running' : 'Stopped';
            
            // Update button states
            document.getElementById('startBtn').disabled = status.running;
            document.getElementById('stopBtn').disabled = !status.running;
        }
        
        async function loadApplicationHistory() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                
                const tbody = document.getElementById('applicationHistory');
                tbody.innerHTML = '';
                
                history.slice(0, 10).forEach(app => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${app.job?.title || 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${app.job?.company || 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${app.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                ${app.success ? 'Success' : 'Failed'}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(app.ai_confidence * 100).toFixed(1)}%</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (error) {
                console.error('Failed to load application history:', error);
            }
        }
        
        async function startAutomation() {
            try {
                const response = await fetch('/api/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        strategy: 'conservative'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Automation started successfully!');
                    loadStatus();
                } else {
                    alert('Failed to start automation: ' + result.message);
                }
            } catch (error) {
                console.error('Failed to start automation:', error);
                alert('Failed to start automation');
            }
        }
        
        async function stopAutomation() {
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Automation stopped successfully!');
                    loadStatus();
                } else {
                    alert('Failed to stop automation: ' + result.message);
                }
            } catch (error) {
                console.error('Failed to stop automation:', error);
                alert('Failed to stop automation');
            }
        }
        
        async function analyzeJob() {
            const jobTitle = document.getElementById('jobTitle').value;
            const jobCompany = document.getElementById('jobCompany').value;
            const jobDescription = document.getElementById('jobDescription').value;
            
            if (!jobTitle || !jobCompany || !jobDescription) {
                alert('Please fill in all fields');
                return;
            }
            
            try {
                const response = await fetch('/api/analyze_job', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        job_data: {
                            title: jobTitle,
                            company: jobCompany,
                            description: jobDescription
                        },
                        user_profile: {
                            // This would come from the actual user profile
                            skills: ['Python', 'JavaScript', 'React'],
                            experience_years: 3,
                            current_title: 'Software Engineer'
                        }
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAnalysisResults(result.analysis);
                } else {
                    alert('Failed to analyze job: ' + result.error);
                }
            } catch (error) {
                console.error('Failed to analyze job:', error);
                alert('Failed to analyze job');
            }
        }
        
        function showAnalysisResults(analysis) {
            const resultsDiv = document.getElementById('analysisResults');
            resultsDiv.innerHTML = `
                <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-4">Analysis Results</h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Overall Score:</span>
                            <span class="text-sm font-medium">${(analysis.overall_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Compatibility:</span>
                            <span class="text-sm font-medium">${(analysis.compatibility_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Skill Match:</span>
                            <span class="text-sm font-medium">${(analysis.skill_match_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Should Apply:</span>
                            <span class="text-sm font-medium ${analysis.should_apply ? 'text-green-600' : 'text-red-600'}">${analysis.should_apply ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                    <div class="mt-4">
                        <p class="text-sm text-gray-600"><strong>Reasoning:</strong> ${analysis.reasoning}</p>
                    </div>
                    <div class="mt-4">
                        <p class="text-sm text-gray-600"><strong>Skill Matches:</strong> ${analysis.skill_matches.join(', ')}</p>
                        <p class="text-sm text-gray-600"><strong>Skill Gaps:</strong> ${analysis.skill_gaps.join(', ')}</p>
                    </div>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        }
    </script>
</body>
</html>
    """
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(template_html)

def create_dashboard_template():
    """Create the dashboard HTML template"""
    template_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LinkedIn Automation Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <div>
                        <h1 class="text-3xl font-bold text-gray-900">LinkedIn Automation Dashboard</h1>
                        <p class="text-gray-600">Real-time monitoring and control</p>
                    </div>
                    <div class="flex space-x-4">
                        <button id="startBtn" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">
                            Start Automation
                        </button>
                        <button id="stopBtn" class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg" disabled>
                            Stop Automation
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- Statistics Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-blue-100 text-blue-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Total Applications</p>
                            <p class="text-2xl font-semibold text-gray-900" id="totalApplications">0</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-green-100 text-green-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Success Rate</p>
                            <p class="text-2xl font-semibold text-gray-900" id="successRate">0%</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-yellow-100 text-yellow-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Running Time</p>
                            <p class="text-2xl font-semibold text-gray-900" id="runningTime">Not running</p>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow p-6">
                    <div class="flex items-center">
                        <div class="p-3 rounded-full bg-purple-100 text-purple-600">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                        </div>
                        <div class="ml-4">
                            <p class="text-sm font-medium text-gray-600">Status</p>
                            <p class="text-2xl font-semibold text-gray-900" id="status">Stopped</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts and Tables -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Application History -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900">Recent Applications</h3>
                    </div>
                    <div class="p-6">
                        <div class="overflow-x-auto">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="bg-gray-50">
                                    <tr>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                                    </tr>
                                </thead>
                                <tbody id="applicationHistory" class="bg-white divide-y divide-gray-200">
                                    <!-- Application history will be populated here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Job Analysis -->
                <div class="bg-white rounded-lg shadow">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-medium text-gray-900">Job Analysis</h3>
                    </div>
                    <div class="p-6">
                        <div id="jobAnalysisForm">
                            <div class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Job Title</label>
                                    <input type="text" id="jobTitle" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Company</label>
                                    <input type="text" id="jobCompany" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                                </div>
                                <div>
                                    <label class="block text-sm font-medium text-gray-700">Job Description</label>
                                    <textarea id="jobDescription" rows="4" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"></textarea>
                                </div>
                                <button id="analyzeJobBtn" class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                                    Analyze Job
                                </button>
                            </div>
                        </div>
                        <div id="analysisResults" class="mt-6 hidden">
                            <!-- Analysis results will be shown here -->
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Dashboard JavaScript
        let statusInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            loadStatus();
            loadApplicationHistory();
            setupEventListeners();
            
            // Update status every 5 seconds
            statusInterval = setInterval(loadStatus, 5000);
        });
        
        function setupEventListeners() {
            document.getElementById('startBtn').addEventListener('click', startAutomation);
            document.getElementById('stopBtn').addEventListener('click', stopAutomation);
            document.getElementById('analyzeJobBtn').addEventListener('click', analyzeJob);
        }
        
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateDashboard(data.statistics, data.status);
            } catch (error) {
                console.error('Failed to load status:', error);
            }
        }
        
        function updateDashboard(stats, status) {
            document.getElementById('totalApplications').textContent = stats.total_applications;
            document.getElementById('successRate').textContent = stats.success_rate + '%';
            document.getElementById('runningTime').textContent = stats.running_time;
            document.getElementById('status').textContent = status.running ? 'Running' : 'Stopped';
            
            // Update button states
            document.getElementById('startBtn').disabled = status.running;
            document.getElementById('stopBtn').disabled = !status.running;
        }
        
        async function loadApplicationHistory() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                
                const tbody = document.getElementById('applicationHistory');
                tbody.innerHTML = '';
                
                history.slice(0, 10).forEach(app => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${app.job?.title || 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${app.job?.company || 'N/A'}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${app.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                ${app.success ? 'Success' : 'Failed'}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${(app.ai_confidence * 100).toFixed(1)}%</td>
                    `;
                    tbody.appendChild(row);
                });
            } catch (error) {
                console.error('Failed to load application history:', error);
            }
        }
        
        async function startAutomation() {
            try {
                const response = await fetch('/api/start', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        strategy: 'conservative'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Automation started successfully!');
                    loadStatus();
                } else {
                    alert('Failed to start automation: ' + result.message);
                }
            } catch (error) {
                console.error('Failed to start automation:', error);
                alert('Failed to start automation');
            }
        }
        
        async function stopAutomation() {
            try {
                const response = await fetch('/api/stop', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Automation stopped successfully!');
                    loadStatus();
                } else {
                    alert('Failed to stop automation: ' + result.message);
                }
            } catch (error) {
                console.error('Failed to stop automation:', error);
                alert('Failed to stop automation');
            }
        }
        
        async function analyzeJob() {
            const jobTitle = document.getElementById('jobTitle').value;
            const jobCompany = document.getElementById('jobCompany').value;
            const jobDescription = document.getElementById('jobDescription').value;
            
            if (!jobTitle || !jobCompany || !jobDescription) {
                alert('Please fill in all fields');
                return;
            }
            
            try {
                const response = await fetch('/api/analyze_job', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        job_data: {
                            title: jobTitle,
                            company: jobCompany,
                            description: jobDescription
                        },
                        user_profile: {
                            // This would come from the actual user profile
                            skills: ['Python', 'JavaScript', 'React'],
                            experience_years: 3,
                            current_title: 'Software Engineer'
                        }
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAnalysisResults(result.analysis);
                } else {
                    alert('Failed to analyze job: ' + result.error);
                }
            } catch (error) {
                console.error('Failed to analyze job:', error);
                alert('Failed to analyze job');
            }
        }
        
        function showAnalysisResults(analysis) {
            const resultsDiv = document.getElementById('analysisResults');
            resultsDiv.innerHTML = `
                <div class="bg-gray-50 rounded-lg p-4">
                    <h4 class="font-medium text-gray-900 mb-4">Analysis Results</h4>
                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Overall Score:</span>
                            <span class="text-sm font-medium">${(analysis.overall_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Compatibility:</span>
                            <span class="text-sm font-medium">${(analysis.compatibility_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Skill Match:</span>
                            <span class="text-sm font-medium">${(analysis.skill_match_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-sm text-gray-600">Should Apply:</span>
                            <span class="text-sm font-medium ${analysis.should_apply ? 'text-green-600' : 'text-red-600'}">${analysis.should_apply ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                    <div class="mt-4">
                        <p class="text-sm text-gray-600"><strong>Reasoning:</strong> ${analysis.reasoning}</p>
                    </div>
                    <div class="mt-4">
                        <p class="text-sm text-gray-600"><strong>Skill Matches:</strong> ${analysis.skill_matches.join(', ')}</p>
                        <p class="text-sm text-gray-600"><strong>Skill Gaps:</strong> ${analysis.skill_gaps.join(', ')}</p>
                    </div>
                </div>
            `;
            resultsDiv.classList.remove('hidden');
        }
    </script>
</body>
</html>
    """
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(template_html) 
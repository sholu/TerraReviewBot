#!/usr/bin/env python3
"""
TerraReviewBot - AI-Powered Terraform Plan Validator
Simple Flask application for validating and analyzing Terraform plans
"""

import os
import json
import logging
from flask import Flask, request, render_template, jsonify, flash, redirect, url_for, session
from werkzeug.utils import secure_filename

# AI integration
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = os.urandom(24)  # Required for sessions

# Setup logging  
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions - only text and JSON formats
ALLOWED_EXTENSIONS = {'json', 'txt'}

def allowed_file(filename):
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_terraform_plan_json(file_path):
    """Validate Terraform JSON plan file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check for Terraform plan structure
        terraform_fields = ['terraform_version', 'format_version', 'resource_changes', 'planned_values']
        if any(field in data for field in terraform_fields):
            return True, "Valid Terraform JSON plan detected", data
        else:
            return False, "JSON does not contain Terraform plan structure", None
            
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}", None
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None

def analyze_with_ai(plan_data, api_key):
    """Analyze Terraform plan using NVIDIA AI."""
    if not api_key:
        return None, "No API key provided. Please enter your NVIDIA API key to enable AI analysis."
    
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        # Create a summary for AI analysis
        plan_summary = str(plan_data)[:1000] if plan_data else "No plan data"
        
        prompt = f"""
        Analyze this Terraform plan and provide a clean, well-formatted summary:
        
        Plan Details: {plan_summary}
        
        Please format your response exactly like this structure (no # symbols, clean headers with colons):

        Overview:
        Brief description of what this plan will accomplish.

        Key Resources:
        Creating:
        • Resource 1 - description
        • Resource 2 - description

        Modifying:
        • Resource 1 - description (if any)

        Destroying:
        • Resource 1 - description (if any)

        Security & Risk Assessment:
        • Risk 1 - description and impact
        • Risk 2 - description and mitigation

        Cost Impact:
        • Brief cost analysis and considerations

        Next Steps:
        • Step 1 - what to do next
        • Step 2 - monitoring recommendations

        Keep it concise, use consistent bullet points (•), and clean headers ending with colons only.
        """
        
        completion = client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-nano-8b-v1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400
        )
        
        return completion.choices[0].message.content, None
        
    except Exception as e:
        return None, f"AI analysis error: {str(e)}"

def validate_terraform_plan_text(file_path):
    """Validate Terraform text plan file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common Terraform plan text indicators
        terraform_indicators = [
            'Terraform will perform the following actions:',
            'Plan:',
            'resource "',
            'data "',
            '# will be created',
            '# will be destroyed',
            '# will be updated',
            'terraform plan',
            'No changes. Infrastructure is up-to-date.'
        ]
        
        # Check if content contains terraform plan indicators
        if any(indicator in content for indicator in terraform_indicators):
            return True, "Valid Terraform text plan detected", {'content': content[:1000]}  # First 1000 chars for analysis
        else:
            return False, "Text does not appear to be a Terraform plan output", None
            
    except UnicodeDecodeError as e:
        return False, f"Unable to decode text file: {str(e)}", None
    except Exception as e:
        return False, f"Error reading file: {str(e)}", None

@app.route('/')
def index():
    """Home page with upload form."""
    return render_template('index.html', stored_api_key=session.get('api_key', ''))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and validation."""
    try:
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Determine validation approach based on file extension
            if filename.lower().endswith('.json'):
                is_valid, message, plan_data = validate_terraform_plan_json(filepath)
            else:
                # For .txt files (text plan output)
                is_valid, message, plan_data = validate_terraform_plan_text(filepath)
            
            # Handle API key - store in session if provided, otherwise use from session
            api_key = request.form.get('api_key', '').strip()
            if api_key:
                session['api_key'] = api_key  # Store in Flask session
            else:
                api_key = session.get('api_key', '')  # Retrieve from Flask session
            
            # Generate AI analysis if validation successful
            ai_analysis = None
            ai_error = None
            
            if is_valid and plan_data:
                ai_analysis, ai_error = analyze_with_ai(plan_data, api_key)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            # Create validation object for template
            validation = {
                'is_valid': is_valid,
                'message': message,
                'file_type': 'JSON' if filename.lower().endswith('.json') else 'Text',
                'plan_data': plan_data,
                'show_plan_summary': filename.lower().endswith('.json')  # Only show for JSON files
            }
            
            # Format AI analysis for better display
            formatted_analysis = None
            ai_result = None
            
            if ai_analysis:
                formatted_analysis = ai_analysis
                # Clean up the response - remove stray # symbols and format properly
                formatted_analysis = formatted_analysis.replace('\n#\n', '\n')  # Remove standalone #
                formatted_analysis = formatted_analysis.replace('\n# ', '\n')   # Remove # at start of lines
                formatted_analysis = formatted_analysis.replace('##', '')       # Remove any remaining ##
                
                # Convert to simple HTML with clean formatting
                lines = formatted_analysis.split('\n')
                html_lines = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    elif line.endswith(':') and not line.startswith('•'):
                        # Main headers (Overview, Key Resources, etc.)
                        html_lines.append(f'<h4 class="text-primary mt-4 mb-2">{line[:-1]}</h4>')
                    elif line.startswith('•'):
                        # Bullet points
                        html_lines.append(f'<div class="ms-3 mb-1">{line}</div>')
                    else:
                        # Regular text
                        html_lines.append(f'<p class="mb-2">{line}</p>')
                
                formatted_analysis = '\n'.join(html_lines)
                ai_result = {'success': True, 'analysis': formatted_analysis}
            elif ai_error:
                ai_result = {'success': False, 'error': ai_error}
            
            return render_template('result.html', 
                                 filename=filename,
                                 validation=validation,
                                 ai_analysis=ai_analysis,
                                 ai_result=ai_result,
                                 has_api_key=bool(session.get('api_key')))
        else:
            flash('File type not allowed. Please upload .json or .txt files only. Generate files using: "terraform plan > plan.txt" or "terraform plan -out=plan.tfplan && terraform show -json plan.tfplan > plan.json"')
            return redirect(request.url)
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

@app.route('/api/validate', methods=['POST'])
def api_validate():
    """API endpoint for file validation."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Validate based on file type
        if filename.lower().endswith('.json'):
            is_valid, message, plan_data = validate_terraform_plan_json(filepath)
        else:
            is_valid, message, plan_data = validate_terraform_plan_text(filepath)
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            'filename': filename,
            'is_valid': is_valid,
            'message': message,
            'has_plan_data': plan_data is not None
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-api-key', methods=['POST'])
def clear_api_key():
    """Clear API key from session."""
    session.pop('api_key', None)
    flash('API key cleared from session')
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"Starting TerraReviewBot on port {port}...")
    app.run(debug=True, host='0.0.0.0', port=port)
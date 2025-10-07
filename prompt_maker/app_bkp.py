from fasthtml.common import *
from monsterui.all import *
import os
import asyncio
from dotenv import load_dotenv
import litellm
import json

# Load environment variables
load_dotenv()

# App setup with MonsterUI blue theme
app,rt = fast_app(
    hdrs=Theme.blue.headers(),
    live=True,   # Enable live reload
    debug=True   # Enable debug mode for better error messages
)

# Define the 7 core prompt components
prompt_components = [
    ("role", "Role & Persona", "Define the AI's role, expertise, and perspective"),
    ("task", "Task Definition", "Clearly specify what you want the AI to do"),
    ("context", "Context & Background", "Provide relevant information and constraints"),
    ("format", "Output Format", "Specify how you want the response structured"),
    ("examples", "Examples", "Include sample inputs/outputs for clarity"),
    ("constraints", "Constraints & Rules", "Set boundaries and limitations"),
    ("evaluation", "Success Criteria", "Define how to measure quality output")
]

# Define available LLM models and providers (LiteLLM compatible)
llm_models = [
    ("gpt-4", "GPT-4", "Most capable, best for complex tasks"),
    ("gpt-3.5-turbo", "GPT-3.5 Turbo", "Fast and efficient for most tasks"),
    ("claude-3-opus-20240229", "Claude 3 Opus", "Excellent for analysis and reasoning"),
    ("claude-3-sonnet-20240229", "Claude 3 Sonnet", "Balanced performance and speed"),
    ("claude-3-haiku-20240307", "Claude 3 Haiku", "Fastest, good for simple tasks"),
    ("gemini-pro", "Gemini Pro", "Google's flagship model"),
]

# Enhanced prompt templates based on components
prompt_templates = {
    "role": "You are a {expertise} with deep knowledge in {domain}. Your approach is {style} and you always {approach}.",
    "task": "Your primary objective is: {task}\n\nKey requirements:\n{requirements}",
    "context": "Context and Background:\n{context}\n\nRelevant constraints: {constraints}",
    "format": "Please structure your response as follows:\n{format_structure}",
    "examples": "For reference, here are examples of the expected output:\n{examples}",
    "constraints": "Important constraints and limitations:\n{constraints}",
    "evaluation": "Success will be measured by:\n{success_criteria}"
}

# Pre-defined template presets for common use cases
template_presets = [
    {
        "name": "📝 Content Creator",
        "description": "For blogs, articles, and written content",
        "components": ["role", "task", "format", "constraints"],
        "category": "Writing"
    },
    {
        "name": "🎓 Educational Tutor", 
        "description": "For teaching and explaining concepts",
        "components": ["role", "task", "examples", "format", "evaluation"],
        "category": "Education"
    },
    {
        "name": "💼 Business Analyst",
        "description": "For business analysis and strategy",
        "components": ["role", "task", "context", "format", "constraints"],
        "category": "Business"
    },
    {
        "name": "🔧 Code Assistant",
        "description": "For programming and technical help",
        "components": ["role", "task", "examples", "constraints", "evaluation"],
        "category": "Technical"
    },
    {
        "name": "🎨 Creative Writer",
        "description": "For creative and narrative content",
        "components": ["role", "task", "format", "examples"],
        "category": "Creative"
    },
    {
        "name": "📊 Data Analyst",
        "description": "For data analysis and insights",
        "components": ["role", "task", "context", "format", "evaluation"],
        "category": "Analytics"
    }
]

def component_selector():
    """Build the component selection interface"""
    return Div(
        # Template presets section
        Div(
            H4("Quick Templates", cls='mb-2'),
            Select(
                Option("Select a template preset...", value="", selected=True),
                *[Option(f"{preset['name']} - {preset['description']}", value=i) 
                  for i, preset in enumerate(template_presets)],
                id="template_preset",
                onchange="applyTemplate()",
                cls='w-full mb-3'
            ),
            DivFullySpaced(
                Button("Save as Template", cls=(ButtonT.sm, ButtonT.ghost), 
                       onclick="saveTemplate()"),
                Button("Manage Templates", cls=(ButtonT.sm, ButtonT.ghost), 
                       onclick="showTemplateManager()"),
                cls='mb-4'
            ),
            cls='mb-4 p-3 border rounded-lg bg-muted/5'
        ),
        
        # Select All / Clear All buttons
        DivFullySpaced(
            Button("Select All", cls=(ButtonT.sm, ButtonT.ghost), 
                   onclick="selectAll()"),
            Button("Clear All", cls=(ButtonT.sm, ButtonT.ghost), 
                   onclick="clearAll()"),
            cls='mb-4'),
        
        # Component checkboxes
        Div(*[
            LabelCheckboxX(
                Div(Strong(title), P(desc, cls=TextPresets.muted_sm)),
                id=f"comp_{comp_id}",
                name="components",
                value=comp_id,
                cls='mb-3 p-2 rounded border hover:bg-muted'
            ) for comp_id, title, desc in prompt_components
        ]),
        
        # Custom conditions textarea
        Div(
            FormLabel("Custom Conditions", cls='mt-4 mb-2'),
            TextArea(
                placeholder="Add any additional conditions or specific requirements...",
                id="custom_conditions",
                cls='min-h-24',
                rows=3
            ),
            cls='mt-6'
        ),
        
        # JavaScript for Select All / Clear All and Templates
        Script(f"""
            // Template presets data
            const templatePresets = {json.dumps(template_presets)};
            
            function selectAll() {{
                document.querySelectorAll('input[name="components"]').forEach(cb => cb.checked = true);
            }}
            function clearAll() {{
                document.querySelectorAll('input[name="components"]').forEach(cb => cb.checked = false);
            }}
            
            function applyTemplate() {{
                const select = document.getElementById('template_preset');
                const index = select.value;
                
                if (index === '') return;
                
                const template = templatePresets[index];
                
                // Clear all first
                clearAll();
                
                // Apply template components
                template.components.forEach(component => {{
                    const checkbox = document.getElementById(`comp_${{component}}`);
                    if (checkbox) checkbox.checked = true;
                }});
                
                // Show feedback
                const option = select.options[select.selectedIndex];
                alert(`Applied template: ${{template.name}}`);
                
                // Reset selection
                select.value = '';
            }}
            
            function saveTemplate() {{
                const selectedComponents = Array.from(document.querySelectorAll('input[name="components"]:checked'))
                    .map(cb => cb.value);
                
                if (selectedComponents.length === 0) {{
                    alert('Please select some components first!');
                    return;
                }}
                
                const name = prompt('Template name:');
                if (!name) return;
                
                const description = prompt('Template description:');
                if (!description) return;
                
                const category = prompt('Category (e.g., Writing, Technical, Business):') || 'Custom';
                
                // Save to localStorage
                const customTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                customTemplates.push({{
                    name: name,
                    description: description,
                    components: selectedComponents,
                    category: category,
                    created: new Date().toLocaleString(),
                    id: Date.now()
                }});
                
                localStorage.setItem('custom_templates', JSON.stringify(customTemplates));
                
                alert(`Template "${{name}}" saved successfully!`);
                updateTemplateDropdown();
            }}
            
            function showTemplateManager() {{
                const customTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                
                if (customTemplates.length === 0) {{
                    alert('No custom templates saved yet. Create one using "Save as Template"!');
                    return;
                }}
                
                let templateList = customTemplates.map((template, index) => 
                    `${{index + 1}}. ${{template.name}} (${{template.category}}) - ${{template.components.length}} components`
                ).join('\\n');
                
                const choice = prompt(`Custom Templates:\\n\\n${{templateList}}\\n\\nEnter template number to delete, or press Cancel:`);
                
                if (choice && !isNaN(choice)) {{
                    const index = parseInt(choice) - 1;
                    if (index >= 0 && index < customTemplates.length) {{
                        const template = customTemplates[index];
                        if (confirm(`Delete template "${{template.name}}"?`)) {{
                            customTemplates.splice(index, 1);
                            localStorage.setItem('custom_templates', JSON.stringify(customTemplates));
                            alert('Template deleted!');
                            updateTemplateDropdown();
                        }}
                    }}
                }}
            }}
            
            function updateTemplateDropdown() {{
                const select = document.getElementById('template_preset');
                const customTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                
                // Clear existing options except first
                while (select.options.length > 1) {{
                    select.removeChild(select.lastChild);
                }}
                
                // Add built-in presets
                templatePresets.forEach((preset, index) => {{
                    const option = new Option(`${{preset.name}} - ${{preset.description}}`, index);
                    select.appendChild(option);
                }});
                
                // Add custom templates
                if (customTemplates.length > 0) {{
                    const separator = new Option('--- Custom Templates ---', '', false, false);
                    separator.disabled = true;
                    select.appendChild(separator);
                    
                    customTemplates.forEach((template, index) => {{
                        const option = new Option(`${{template.name}} - ${{template.description}}`, `custom_${{index}}`);
                        select.appendChild(option);
                    }});
                }}
            }}
            
            // Enhanced applyTemplate to handle custom templates
            function applyTemplate() {{
                const select = document.getElementById('template_preset');
                const value = select.value;
                
                if (value === '') return;
                
                let template;
                if (value.startsWith('custom_')) {{
                    const customTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                    const index = parseInt(value.replace('custom_', ''));
                    template = customTemplates[index];
                }} else {{
                    template = templatePresets[value];
                }}
                
                if (!template) return;
                
                // Clear all first
                clearAll();
                
                // Apply template components
                template.components.forEach(component => {{
                    const checkbox = document.getElementById(`comp_${{component}}`);
                    if (checkbox) checkbox.checked = true;
                }});
                
                // Show feedback
                alert(`Applied template: ${{template.name}}`);
                
                // Reset selection
                select.value = '';
            }}
            
            // Initialize template dropdown on page load
            document.addEventListener('DOMContentLoaded', function() {{
                updateTemplateDropdown();
            }});
        """)
    )

def main_input_area():
    """Build the main criteria input interface"""
    placeholder_text = """Examples of effective criteria:

• "Create a Python tutorial for beginners that explains loops with practical examples"
• "Write a professional email declining a job offer while maintaining positive relationships"  
• "Generate a marketing strategy for a sustainable fashion brand targeting Gen Z"
• "Explain quantum computing concepts using simple analogies for non-technical audiences"

Your criteria should be specific, actionable, and include any constraints or preferences..."""

    return Div(
        # Main textarea with auto-resize
        TextArea(
            placeholder=placeholder_text,
            id="main_criteria",
            cls='w-full min-h-80 resize-y',
            rows=12,
            oninput="updateWordCount(); autoSave()",
            onkeyup="updateWordCount()"
        ),
        
        # Word/character count indicator
        Div(
            DivFullySpaced(
                Div(
                    Span("Words: ", cls=TextT.sm),
                    Span("0", id="word-count", cls=(TextT.sm, TextT.medium)),
                    Span(" | Characters: ", cls=TextT.sm),
                    Span("0", id="char-count", cls=(TextT.sm, TextT.medium)),
                    cls='text-muted-foreground'
                ),
                Div(
                    Span("Auto-saved", id="save-status", 
                         cls=(TextT.sm, 'text-green-600', 'opacity-0')),
                )
            ),
            cls='mt-2 px-1'
        ),
        
        # JavaScript for word count and auto-save
        Script("""
            let saveTimeout;
            
            function updateWordCount() {
                const textarea = document.getElementById('main_criteria');
                const text = textarea.value.trim();
                
                const wordCount = text === '' ? 0 : text.split(/\s+/).length;
                const charCount = textarea.value.length;
                
                document.getElementById('word-count').textContent = wordCount;
                document.getElementById('char-count').textContent = charCount;
            }
            
            function autoSave() {
                const status = document.getElementById('save-status');
                status.classList.remove('opacity-0');
                status.textContent = 'Saving...';
                status.className = status.className.replace('text-green-600', 'text-yellow-600');
                
                // Clear existing timeout
                clearTimeout(saveTimeout);
                
                // Set new timeout for auto-save
                saveTimeout = setTimeout(() => {
                    // Simulate save (in real app, this would send to server)
                    localStorage.setItem('prompt_criteria', document.getElementById('main_criteria').value);
                    
                    status.textContent = 'Auto-saved';
                    status.className = status.className.replace('text-yellow-600', 'text-green-600');
                    
                    // Hide status after 2 seconds
                    setTimeout(() => {
                        status.classList.add('opacity-0');
                    }, 2000);
                }, 1000);
            }
            
            // Load saved content on page load
            document.addEventListener('DOMContentLoaded', function() {
                const saved = localStorage.getItem('prompt_criteria');
                if (saved) {
                    document.getElementById('main_criteria').value = saved;
                    updateWordCount();
                }
            });
        """)
    )

def output_panel():
    """Build the output panel with LLM configuration and generation"""
    return Div(
        # LLM Configuration Section
        Div(
            H4("LLM Configuration", cls='mb-3'),
            
            # Model selection dropdown
            LabelSelect(
                *[Option(f"{display_name} - {desc}", value=model)
                  for model, display_name, desc in llm_models],
                label="Model Selection",
                id="llm_model",
                cls='mb-4'
            ),
                     
            # Action buttons
            Grid(
                Button(
                    UkIcon("eye", cls='mr-2'),
                    "Preview",
                    id="preview_btn",
                    cls=(ButtonT.secondary, 'w-full'),
                    onclick="previewPrompt()"
                ),
                Button(
                    UkIcon("wand-2", cls='mr-2'),
                    "Generate with AI",
                    id="generate_btn",
                    cls=(ButtonT.primary, 'w-full'),
                    onclick="generatePrompt()"
                ),
                cols=2, gap=2, cls='mb-3'
            ),
            
            # Status indicator
            DivCentered(
                Span("Ready", id="gen-status", cls=(TextT.sm, 'text-muted-foreground')),
                Loading(cls=(LoadingT.spinner, LoadingT.sm, 'ml-2', 'hidden'), id="gen-spinner")
            ),
            
            cls='mb-6 p-4 border rounded-lg bg-muted/10'
        ),
        
        # Generated prompt output
        Div(
            H4("Generated Prompt", cls='mb-3'),
            TextArea(
                placeholder="Your generated prompt will appear here...",
                id="generated_prompt",
                cls='w-full min-h-64 resize-y',
                rows=10,
                readonly=True
            ),
            
            # Output actions
            Grid(
                Button("Copy", cls=(ButtonT.ghost, ButtonT.sm), onclick="copyPrompt()"),
                Button("Edit", cls=(ButtonT.ghost, ButtonT.sm), onclick="editPrompt()"),
                Button("Export", cls=(ButtonT.ghost, ButtonT.sm), onclick="showExportModal()"),
                Button("Save v1.0", id="save_btn", cls=(ButtonT.secondary, ButtonT.sm), onclick="saveToHistory()"),
                cols=4, gap=2, cls='mt-3'
            ),
            
            cls='mb-4'
        ),
        
        # JavaScript for generation and actions
        Script("""
            function previewPrompt() {
                const output = document.getElementById('generated_prompt');
                const selectedComponents = Array.from(document.querySelectorAll('input[name="components"]:checked'))
                    .map(cb => cb.value);
                const criteria = document.getElementById('main_criteria').value.trim();
                
                if (!criteria) {
                    alert('Please enter your criteria first!');
                    return;
                }
                
                const prompt = buildStructuredPrompt(selectedComponents, criteria);
                output.value = prompt;
                
                // Show preview feedback
                const status = document.getElementById('gen-status');
                status.textContent = 'Preview Generated';
                status.className = status.className.replace('text-muted-foreground', 'text-blue-600');
                setTimeout(() => {
                    status.textContent = 'Ready';
                    status.className = status.className.replace('text-blue-600', 'text-muted-foreground');
                }, 2000);
            }
            
            async function generatePrompt() {
                const btn = document.getElementById('generate_btn');
                const status = document.getElementById('gen-status');
                const spinner = document.getElementById('gen-spinner');
                const output = document.getElementById('generated_prompt');
                
                // Get selected components
                const selectedComponents = Array.from(document.querySelectorAll('input[name="components"]:checked'))
                    .map(cb => cb.value);
                
                // Get main criteria
                const criteria = document.getElementById('main_criteria').value.trim();
                
                if (!criteria) {
                    alert('Please enter your criteria first!');
                    return;
                }
                
                // Get configuration
                const model = document.getElementById('llm_model').value || 'gpt-3.5-turbo';
                const customConditions = document.getElementById('custom_conditions').value || '';
                
                // Update UI for generation
                btn.disabled = true;
                status.textContent = 'Generating with AI...';
                status.className = status.className.replace('text-muted-foreground', 'text-blue-600');
                spinner.classList.remove('hidden');
                
                try {
                    // Call real API
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            components: selectedComponents,
                            criteria: criteria,
                            custom_conditions: customConditions,
                            model: model
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        output.value = result.prompt;
                        status.textContent = 'AI Generation Complete';
                        status.className = status.className.replace('text-blue-600', 'text-green-600');
                    } else {
                        output.value = `Error: ${result.error}`;
                        status.textContent = 'Generation Error';
                        status.className = status.className.replace('text-blue-600', 'text-red-600');
                    }
                } catch (error) {
                    output.value = `Network error: ${error.message}`;
                    status.textContent = 'Network Error';
                    status.className = status.className.replace('text-blue-600', 'text-red-600');
                }
                
                // Reset UI
                btn.disabled = false;
                spinner.classList.add('hidden');
                
                // Auto-hide status after 3 seconds
                setTimeout(() => {
                    status.textContent = 'Ready';
                    status.className = status.className.replace(/text-(green|red)-600/, 'text-muted-foreground');
                }, 3000);
            }
            
            function buildStructuredPrompt(components, criteria) {
                let prompt = `# AI Prompt\\n\\n`;
                
                if (components.includes('role')) {
                    prompt += `## Role & Persona\\nAct as an expert in the relevant field with deep knowledge and experience.\\n\\n`;
                }
                
                if (components.includes('task')) {
                    prompt += `## Task\\n${criteria}\\n\\n`;
                }
                
                if (components.includes('context')) {
                    prompt += `## Context\\nConsider the broader context and background information relevant to this task.\\n\\n`;
                }
                
                if (components.includes('format')) {
                    prompt += `## Output Format\\nProvide a clear, well-structured response that is easy to understand and actionable.\\n\\n`;
                }
                
                if (components.includes('examples')) {
                    prompt += `## Examples\\nInclude relevant examples to illustrate key points where appropriate.\\n\\n`;
                }
                
                if (components.includes('constraints')) {
                    prompt += `## Constraints\\nEnsure the response is accurate, helpful, and follows best practices.\\n\\n`;
                }
                
                if (components.includes('evaluation')) {
                    prompt += `## Success Criteria\\nThe response should be comprehensive, actionable, and directly address the stated requirements.\\n\\n`;
                }
                
                // Add custom conditions if present
                const customConditions = document.getElementById('custom_conditions').value.trim();
                if (customConditions) {
                    prompt += `## Additional Requirements\\n${customConditions}\\n\\n`;
                }
                
                return prompt;
            }
            
            function copyPrompt() {
                const output = document.getElementById('generated_prompt');
                output.select();
                document.execCommand('copy');
                
                // Show temporary feedback
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = originalText, 1500);
            }
            
            function editPrompt() {
                const output = document.getElementById('generated_prompt');
                output.readOnly = !output.readOnly;
                
                const btn = event.target;
                btn.textContent = output.readOnly ? 'Edit' : 'Lock';
            }
            
            function saveToHistory() {
                const prompt = document.getElementById('generated_prompt').value;
                if (!prompt.trim()) {
                    alert('No prompt to save!');
                    return;
                }
                
                // Get existing history and calculate next version
                const history = JSON.parse(localStorage.getItem('prompt_history') || '[]');
                const criteria = document.getElementById('main_criteria').value;
                
                // Find similar prompts (same criteria) to determine version
                const similarPrompts = history.filter(h => h.criteria === criteria);
                const nextVersion = `v${similarPrompts.length + 1}.0`;
                
                // Create new prompt entry
                const newPrompt = {
                    id: Date.now(),
                    version: nextVersion,
                    prompt: prompt,
                    timestamp: new Date().toLocaleString(),
                    criteria: criteria,
                    components: Array.from(document.querySelectorAll('input[name="components"]:checked')).map(cb => cb.value),
                    model: document.getElementById('llm_model').value || 'gpt-3.5-turbo',
                    wordCount: prompt.trim().split(/\s+/).length,
                    charCount: prompt.length
                };
                
                history.unshift(newPrompt);
                localStorage.setItem('prompt_history', JSON.stringify(history.slice(0, 20))); // Keep 20 prompts
                
                // Update button to show next version
                const btn = document.getElementById('save_btn');
                const nextVersionNumber = `v${similarPrompts.length + 2}.0`;
                btn.textContent = `Save ${nextVersionNumber}`;
                
                // Show feedback
                const originalText = btn.textContent;
                btn.textContent = `Saved ${nextVersion}!`;
                setTimeout(() => btn.textContent = originalText, 2000);
                
                // Update history display if visible
                updateHistoryDisplay();
            }
            
            function showExportModal() {
                const prompt = document.getElementById('generated_prompt').value;
                if (!prompt.trim()) {
                    alert('No prompt to export!');
                    return;
                }
                
                // Create modal content
                const modalContent = `
                    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;" onclick="closeExportModal()">
                        <div style="background: white; padding: 2rem; border-radius: 8px; max-width: 500px; width: 90%;" onclick="event.stopPropagation();">
                            <h3 style="margin-top: 0;">Export Prompt</h3>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                                <button onclick="exportAs('text')" style="padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; background: #f8f9fa;">Plain Text</button>
                                <button onclick="exportAs('markdown')" style="padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; background: #f8f9fa;">Markdown</button>
                                <button onclick="exportAs('json')" style="padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; background: #f8f9fa;">JSON</button>
                                <button onclick="exportAs('copy')" style="padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; background: #e3f2fd;">Copy to Clipboard</button>
                            </div>
                            <button onclick="closeExportModal()" style="width: 100%; padding: 0.5rem; border: 1px solid #ccc; border-radius: 4px; background: #f5f5f5;">Close</button>
                        </div>
                    </div>
                `;
                
                // Add modal to page
                const modal = document.createElement('div');
                modal.id = 'export-modal';
                modal.innerHTML = modalContent;
                document.body.appendChild(modal);
            }
            
            function closeExportModal() {
                const modal = document.getElementById('export-modal');
                if (modal) modal.remove();
            }
            
            function exportAs(format) {
                const prompt = document.getElementById('generated_prompt').value;
                const criteria = document.getElementById('main_criteria').value;
                const timestamp = new Date().toLocaleString();
                const components = Array.from(document.querySelectorAll('input[name="components"]:checked')).map(cb => cb.value);
                
                let content, filename, mimeType;
                
                switch (format) {
                    case 'text':
                        content = prompt;
                        filename = `prompt_${Date.now()}.txt`;
                        mimeType = 'text/plain';
                        break;
                        
                    case 'markdown':
                        content = `# AI Prompt Export\\n\\n**Generated:** ${timestamp}\\n**Components:** ${components.join(', ')}\\n\\n## Original Criteria\\n${criteria}\\n\\n## Generated Prompt\\n${prompt}`;
                        filename = `prompt_${Date.now()}.md`;
                        mimeType = 'text/markdown';
                        break;
                        
                    case 'json':
                        content = JSON.stringify({
                            timestamp,
                            criteria,
                            components,
                            prompt,
                            metadata: {
                                wordCount: prompt.trim().split(/\s+/).length,
                                charCount: prompt.length,
                                model: document.getElementById('llm_model').value
                            }
                        }, null, 2);
                        filename = `prompt_${Date.now()}.json`;
                        mimeType = 'application/json';
                        break;
                        
                    case 'copy':
                        navigator.clipboard.writeText(prompt).then(() => {
                            alert('Prompt copied to clipboard!');
                        });
                        closeExportModal();
                        return;
                }
                
                // Download file
                const blob = new Blob([content], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
                
                closeExportModal();
            }
            
            function updateHistoryDisplay() {
                const history = JSON.parse(localStorage.getItem('prompt_history') || '[]');
                const count = document.getElementById('history_count');
                const historyList = document.getElementById('history_list');
                
                // Update count
                count.textContent = `${history.length} saved`;
                
                // Update history list
                if (history.length === 0) {
                    historyList.innerHTML = '<p class="text-muted-foreground">No prompts saved yet. Generate and save prompts to see them here.</p>';
                } else {
                    historyList.innerHTML = history.slice(0, 5).map(item => `
                        <div class="border-b pb-3 mb-3 cursor-pointer hover:bg-muted p-2 rounded" onclick="loadPrompt(${item.id})">
                            <div class="flex justify-between items-start mb-1">
                                <strong class="text-sm">${item.version}</strong>
                                <small class="text-muted-foreground">${item.timestamp}</small>
                            </div>
                            <div class="text-sm text-muted-foreground mb-1">
                                Model: ${item.model} | ${item.wordCount} words
                            </div>
                            <div class="text-sm line-clamp-2">${item.criteria.substring(0, 100)}${item.criteria.length > 100 ? '...' : ''}</div>
                        </div>
                    `).join('');
                    
                    if (history.length > 5) {
                        historyList.innerHTML += `<p class="text-center text-muted-foreground text-sm">And ${history.length - 5} more...</p>`;
                    }
                }
            }
            
            function toggleHistory() {
                const panel = document.getElementById('history_panel');
                const btn = document.getElementById('history_btn');
                
                if (panel.classList.contains('hidden')) {
                    panel.classList.remove('hidden');
                    btn.textContent = '︽ Hide History';
                    updateHistoryDisplay();
                } else {
                    panel.classList.add('hidden');
                    btn.innerHTML = '<svg class="w-4 h-4 mr-2" fill="currentColor"><use href="#history"></use></svg>History';
                }
            }
            
            function loadPrompt(promptId) {
                const history = JSON.parse(localStorage.getItem('prompt_history') || '[]');
                const prompt = history.find(p => p.id === promptId);
                
                if (prompt) {
                    // Load prompt data
                    document.getElementById('main_criteria').value = prompt.criteria;
                    document.getElementById('generated_prompt').value = prompt.prompt;
                    
                    // Update component selection
                    document.querySelectorAll('input[name="components"]').forEach(cb => {
                        cb.checked = prompt.components.includes(cb.value);
                    });
                    
                    // Update model selection
                    document.getElementById('llm_model').value = prompt.model;
                    
                    // Update word count
                    updateWordCount();
                    
                    // Hide history panel
                    toggleHistory();
                    
                    alert(`Loaded ${prompt.version} from ${prompt.timestamp}`);
                }
            }
            
            function exportTemplates() {
                const customTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                
                if (customTemplates.length === 0) {
                    alert('No custom templates to export. Create some templates first!');
                    return;
                }
                
                const exportData = {
                    templates: customTemplates,
                    exported: new Date().toISOString(),
                    version: '1.0',
                    app: 'AI Prompt Maker'
                };
                
                const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `prompt_templates_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                alert(`Exported ${customTemplates.length} templates successfully!`);
            }
            
            function importTemplates() {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.onchange = function(event) {
                    const file = event.target.files[0];
                    if (!file) return;
                    
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        try {
                            const importData = JSON.parse(e.target.result);
                            
                            if (!importData.templates || !Array.isArray(importData.templates)) {
                                alert('Invalid template file format!');
                                return;
                            }
                            
                            const existingTemplates = JSON.parse(localStorage.getItem('custom_templates') || '[]');
                            const newTemplates = importData.templates;
                            
                            // Ask user about merge strategy
                            const choice = confirm(`Import ${newTemplates.length} templates?\\n\\nOK = Merge with existing\\nCancel = Replace all existing`);
                            
                            let finalTemplates;
                            if (choice) {
                                // Merge - avoid duplicates by name
                                const existingNames = existingTemplates.map(t => t.name);
                                const uniqueNew = newTemplates.filter(t => !existingNames.includes(t.name));
                                finalTemplates = [...existingTemplates, ...uniqueNew];
                                
                                if (uniqueNew.length < newTemplates.length) {
                                    alert(`Imported ${uniqueNew.length} new templates. ${newTemplates.length - uniqueNew.length} were skipped (duplicates).`);
                                } else {
                                    alert(`Imported ${uniqueNew.length} templates successfully!`);
                                }
                            } else {
                                // Replace
                                finalTemplates = newTemplates;
                                alert(`Replaced all templates with ${newTemplates.length} imported templates!`);
                            }
                            
                            localStorage.setItem('custom_templates', JSON.stringify(finalTemplates));
                            updateTemplateDropdown();
                            
                        } catch (error) {
                            alert('Error reading template file: ' + error.message);
                        }
                    };
                    reader.readAsText(file);
                };
                input.click();
            }
            
            function showHelp() {
                const helpContent = `
                    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 2000; display: flex; align-items: center; justify-content: center;" onclick="closeHelp()">
                        <div style="background: white; padding: 2rem; border-radius: 12px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto;" onclick="event.stopPropagation();">
                            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                                <h2 style="margin: 0;">🚀 AI Prompt Maker - Quick Help</h2>
                                <button onclick="closeHelp()" style="background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; padding: 0.5rem; cursor: pointer;">✕</button>
                            </div>
                            
                            <div style="space-y: 1rem;">
                                <div>
                                    <h3 style="color: #2563eb; margin-bottom: 0.5rem;">⌨️ Keyboard Shortcuts</h3>
                                    <div style="font-family: monospace; font-size: 0.9rem; line-height: 1.6;">
                                        <div><strong>Ctrl+P</strong> - Preview prompt</div>
                                        <div><strong>Ctrl+G</strong> - Generate with AI</div>
                                        <div><strong>Ctrl+S</strong> - Save to history</div>
                                        <div><strong>Ctrl+H</strong> - Toggle history</div>
                                        <div><strong>Ctrl+E</strong> - Export prompt</div>
                                        <div><strong>Ctrl+A</strong> - Select all components</div>
                                        <div><strong>Ctrl+D</strong> - Clear all components</div>
                                        <div><strong>?</strong> - Show this help</div>
                                        <div><strong>Escape</strong> - Close modals</div>
                                    </div>
                                </div>
                                
                                <div>
                                    <h3 style="color: #2563eb; margin-bottom: 0.5rem;">📝 Quick Start</h3>
                                    <ol style="padding-left: 1.2rem; line-height: 1.6;">
                                        <li>Choose a template or select components manually</li>
                                        <li>Enter your criteria in the main text area</li>
                                        <li>Click Preview for instant results or Generate with AI for enhanced prompts</li>
                                        <li>Save your prompts and export them for later use</li>
                                    </ol>
                                </div>
                                
                                <div>
                                    <h3 style="color: #2563eb; margin-bottom: 0.5rem;">💡 Pro Tips</h3>
                                    <ul style="padding-left: 1.2rem; line-height: 1.6;">
                                        <li>Use templates for consistent prompt structures</li>
                                        <li>Save custom templates for your specific use cases</li>
                                        <li>Export templates to share with your team</li>
                                        <li>Version numbering helps track prompt iterations</li>
                                        <li>Custom conditions add specific requirements</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                const modal = document.createElement('div');
                modal.id = 'help-modal';
                modal.innerHTML = helpContent;
                document.body.appendChild(modal);
            }
            
            function closeHelp() {
                const modal = document.getElementById('help-modal');
                if (modal) modal.remove();
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Don't trigger shortcuts when typing in inputs
                if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') {
                    return;
                }
                
                if (e.ctrlKey || e.metaKey) {
                    switch(e.key) {
                        case 'p':
                            e.preventDefault();
                            previewPrompt();
                            break;
                        case 'g':
                            e.preventDefault();
                            generatePrompt();
                            break;
                        case 's':
                            e.preventDefault();
                            saveToHistory();
                            break;
                        case 'h':
                            e.preventDefault();
                            toggleHistory();
                            break;
                        case 'e':
                            e.preventDefault();
                            showExportModal();
                            break;
                        case 'a':
                            e.preventDefault();
                            selectAll();
                            break;
                        case 'd':
                            e.preventDefault();
                            clearAll();
                            break;
                    }
                } else if (e.key === '?') {
                    e.preventDefault();
                    showHelp();
                } else if (e.key === 'Escape') {
                    // Close any open modals
                    closeHelp();
                    closeExportModal();
                }
            });
            
            // Enhanced loading states
            function showLoading(element, text = 'Loading...') {
                const loadingSpinner = element.querySelector('.loading-spinner') || document.createElement('div');
                loadingSpinner.className = 'loading-spinner';
                loadingSpinner.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; padding: 1rem;">
                        <div style="width: 20px; height: 20px; border: 2px solid #f3f3f3; border-top: 2px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 0.5rem;"></div>
                        <span>${text}</span>
                    </div>
                `;
                if (!element.querySelector('.loading-spinner')) {
                    element.appendChild(loadingSpinner);
                }
            }
            
            function hideLoading(element) {
                const spinner = element.querySelector('.loading-spinner');
                if (spinner) spinner.remove();
            }
            
            // Add CSS for spinner animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                .tooltip {
                    position: relative;
                    display: inline-block;
                }
                .tooltip .tooltiptext {
                    visibility: hidden;
                    width: 200px;
                    background-color: #333;
                    color: #fff;
                    text-align: center;
                    border-radius: 6px;
                    padding: 5px;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%;
                    left: 50%;
                    margin-left: -100px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    font-size: 0.8rem;
                }
                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
            `;
            document.head.appendChild(style);
            
            // Initialize history display and other features on page load
            document.addEventListener('DOMContentLoaded', function() {
                updateHistoryDisplay();
                
                // Add tooltips to buttons
                addTooltips();
                
                // Show welcome message for first-time users
                if (!localStorage.getItem('has_visited')) {
                    setTimeout(() => {
                        if (confirm('Welcome to AI Prompt Maker! 🎉\\n\\nWould you like to see a quick tour of the features?')) {
                            showHelp();
                        }
                        localStorage.setItem('has_visited', 'true');
                    }, 1000);
                }
            });
            
            function addTooltips() {
                // Add tooltips to key elements
                const tooltips = {
                    'generate_btn': 'Generate enhanced prompt using AI (Ctrl+G)',
                    'preview_btn': 'Quick preview of structured prompt (Ctrl+P)', 
                    'save_btn': 'Save this prompt to history (Ctrl+S)',
                    'history_btn': 'View saved prompts (Ctrl+H)',
                    'template_preset': 'Quick-apply common component combinations'
                };
                
                Object.entries(tooltips).forEach(([id, text]) => {
                    const element = document.getElementById(id);
                    if (element && !element.title) {
                        element.title = text;
                    }
                });
            }
        """)
    )

async def generate_with_llm(model, prompt, temperature=0.7, max_tokens=1000):
    """Generate prompt using LiteLLM"""
    try:
        # Set up LiteLLM with OpenAI API key
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        
        response = await litellm.acompletion(
            model=model,
            messages=[{
                "role": "user", 
                "content": f"""You are a prompt engineering expert. Create a high-quality, structured prompt based on these requirements:

{prompt}

Generate a professional prompt that incorporates the selected components effectively. The output should be ready to use with any LLM."""
            }],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating prompt: {str(e)}"

@rt("/api/generate", methods=["POST"])
async def api_generate(data: dict):
    """API endpoint for prompt generation"""
    try:
        # Extract data from request
        components = data.get("components", [])
        criteria = data.get("criteria", "")
        custom_conditions = data.get("custom_conditions", "")
        model = data.get("model", "gpt-3.5-turbo")
        
        # Use sensible defaults for temperature and tokens
        temperature = 0.7  # Good balance of creativity and coherence
        max_tokens = 1000  # Sufficient for most prompts
        
        # Build initial prompt
        initial_prompt = build_structured_prompt(components, criteria, custom_conditions)
        
        # Generate enhanced prompt using LLM
        enhanced_prompt = await generate_with_llm(model, initial_prompt, temperature, max_tokens)
        
        return {"success": True, "prompt": enhanced_prompt}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def build_structured_prompt(components, criteria, custom_conditions=""):
    """Build a structured prompt from components and criteria"""
    prompt_parts = []
    
    if "role" in components:
        prompt_parts.append("## Role & Persona\nAct as an expert in the relevant field with deep knowledge and experience.")
    
    if "task" in components:
        prompt_parts.append(f"## Task\n{criteria}")
    
    if "context" in components:
        prompt_parts.append("## Context\nConsider the broader context and background information relevant to this task.")
    
    if "format" in components:
        prompt_parts.append("## Output Format\nProvide a clear, well-structured response that is easy to understand and actionable.")
    
    if "examples" in components:
        prompt_parts.append("## Examples\nInclude relevant examples to illustrate key points where appropriate.")
    
    if "constraints" in components:
        prompt_parts.append("## Constraints\nEnsure the response is accurate, helpful, and follows best practices.")
    
    if "evaluation" in components:
        prompt_parts.append("## Success Criteria\nThe response should be comprehensive, actionable, and directly address the stated requirements.")
    
    if custom_conditions:
        prompt_parts.append(f"## Additional Requirements\n{custom_conditions}")
    
    return "\n\n".join(prompt_parts)

@rt
def index():
    """Main prompt maker interface"""
    return Titled("Prompt Maker",
        Container(
            # Header section
            DivFullySpaced(
                Div(
                    H1("AI Prompt Maker"),
                    Subtitle("Create structured prompts for LLM interactions • Press ? for help"),
                ),
                Div(
                    Button(
                        UkIcon("download", cls='mr-1'),
                        "Import Templates",
                        cls=(ButtonT.ghost, ButtonT.sm),
                        onclick="importTemplates()"
                    ),
                    Button(
                        UkIcon("upload", cls='mr-1'),
                        "Export Templates", 
                        cls=(ButtonT.ghost, ButtonT.sm),
                        onclick="exportTemplates()"
                    ),
                    Button(
                        UkIcon("history", cls='mr-1'),
                        "History",
                        id="history_btn",
                        cls=(ButtonT.ghost, ButtonT.sm),
                        onclick="toggleHistory()"
                    ),
                    Span("0 saved", id="history_count", cls=(TextT.sm, 'text-muted-foreground', 'ml-2')),
                    cls='space-x-2'
                ),
                cls='mb-8'),
            
            # History panel (initially hidden)
            Div(
                Card(
                    H4("Prompt History"),
                    Div("No prompts saved yet. Generate and save prompts to see them here.", 
                        id="history_list", cls='text-muted-foreground'),
                    cls='mb-4'
                ),
                id="history_panel",
                cls='hidden'
            ),
            
            # Main layout grid - responsive design
            Grid(
                # Sidebar for components (left column)
                Card(
                    H3("Prompt Components"),
                    P("Select components to include", cls=TextPresets.muted_sm),
                    component_selector(),
                    cls='h-fit',
                    header_cls='pb-4'
                ),
                
                # Main content area (center column)
                Card(
                    H3("Your Criteria"),
                    P("Describe what you want your prompt to achieve", cls=TextPresets.muted_sm),
                    main_input_area(),
                    cls='h-fit',
                    header_cls='pb-4'
                ),
                
                # Output and history (right column)
                Card(
                    H3("Generated Prompt"),
                    P("Configure your LLM and generate structured prompts", cls=TextPresets.muted_sm),
                    output_panel(),
                    cls='h-fit',
                    header_cls='pb-4'
                ),
                
                cols_lg=3, cols_md=1, cols_sm=1, gap=6
            ),
            
            cls=ContainerT.xl
        )
    )

serve()

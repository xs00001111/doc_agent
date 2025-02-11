import os
import asyncio
import gradio as gr
from langchain_openai import ChatOpenAI
from browser_use import Agent
from browser_use.browser.browser import Browser, BrowserConfig
from playwright.sync_api import sync_playwright

def get_chromium_path():
    # Use Playwright to get the path for the installed Chromium browser.
    with sync_playwright() as playwright:
        return playwright.chromium.executable_path()

# Retrieve the Chromium executable path installed by Playwright.
chrome_path = get_chromium_path()

# Set up the browser configuration with the dynamic Chromium path.
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path=chrome_path,
    )
)

# Fill the Google document with the user details
async def fill_content(doc_link, replacements):
    task_description = f'Open {doc_link}'
    
    # Build replacement instructions
    for placeholder, value in replacements.items():
        if value:
            task_description += f' and replace [{placeholder}] with {value}'
    # Initialize the agent for AI explanations
    agent = Agent(
        task=task_description,
        llm=ChatOpenAI(model='gpt-4o'),
        browser=browser,
    )

    # Run the agent
    await agent.run()
    await browser.close()

    return "AI explanations and comments have been added successfully!"

# Generate AI summaries and comments for the document
async def ai_summaries(doc_link):
    task_description = (
        f'Open {doc_link} and read each page, Summarize this contract, including an easy to understand '
        'summary of all the key legal points and not just the terms of the contract (parties, dates, payments, etc). '
        'Comment your summary and explaination on page 1'
    )

    # Initialize the agent for AI summaries
    agent = Agent(
        task=task_description,
        llm=ChatOpenAI(model='gpt-4o'),
        browser=browser,
    )

    # Run the agent
    await agent.run()
    await browser.close()

    return "AI summaries and comments have been added successfully!"

# Custom Task Handling
async def handle_custom_task(doc_link, custom_task):
    task_description = f'{custom_task} in document {doc_link}.'

    # Initialize the agent for custom task
    agent = Agent(
        task=task_description,
        llm=ChatOpenAI(model='gpt-4o'),
        browser=browser,
    )

    # Run the agent
    await agent.run()
    await browser.close()

    return "Custom task completed successfully!"

# Create the Gradio UI
def create_ui():
    with gr.Blocks(title="Document Processor") as interface:
        gr.Markdown("# Google Document Processing with AI")

        with gr.Row():
            with gr.Column():
                doc_link = gr.Textbox(label="Google Document Link", placeholder="Enter the link to your Google Document")
                replacements = gr.Dataframe(
                    headers=["Placeholder", "Value"],
                    datatype=["str", "str"],
                    label="Replacements",
                    col_count=(2, "fixed"),
                    row_count=(3, "dynamic"),
                )
                task_choice = gr.Dropdown(
                    label="Select Task",
                    choices=["Fill Content", "Generate AI Summaries", "Other Updates"],
                    value="Fill Content"
                )
                custom_task = gr.Textbox(
                    label="Custom Task Description",
                    placeholder="Enter your custom task here...",
                    visible=False
                )
                submit_btn = gr.Button("Submit Task")

            with gr.Column():
                output = gr.Textbox(label="Output", lines=10, interactive=False)

            def update_custom_task_visibility(choice):
                return gr.update(visible=choice == "Other Updates")

            task_choice.change(
                fn=update_custom_task_visibility,
                inputs=[task_choice],
                outputs=[custom_task]
            )

            submit_btn.click(
                fn=lambda doc_link, replacements, task_choice, custom_task: (
                    asyncio.run(fill_content(doc_link, dict(zip(replacements['Placeholder'], replacements['Value']))))
                    if task_choice == "Fill Content"
                    else asyncio.run(ai_summaries(doc_link))
                    if task_choice == "Generate AI Summaries"
                    else asyncio.run(handle_custom_task(doc_link, custom_task))
                ),
                inputs=[doc_link, replacements, task_choice, custom_task],
                outputs=output,
            )

    return interface

# Create and launch the UI
demo = create_ui()

# Get the port from the environment variable, defaulting to 7860 for local testing
port = int(os.environ.get("PORT", 7860))

# Launch the Gradio app, binding to 0.0.0.0 and the specified port
demo.queue()  # Enable queuing for concurrent requests
demo.launch(server_name="0.0.0.0", server_port=port, share=True)

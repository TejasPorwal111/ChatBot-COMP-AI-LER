#imports
from dearpygui import dearpygui as dpg
from openai import OpenAI
import threading
import pyperclip

#OpenAi API initilization
client = OpenAI(
    base_url="https://api.sree.shop/v1",
    api_key="ddc-57Zl6umR90Zp9wnmZVJE3hsrr8RjDtPPEk2N7Cr6blgUIEUPdI"
)

#Models
Models = ["gpt-4o" , "claude-3.5-sonnet" , "DeepSeek-R1", "deepseek-v3" , "Meta-Llama"]

#Get Ai response function to send Ai our prompt for getting response
def get_ai_response(question, tech_stack, model="gpt-4o-2024-05-13"):
    prompt = f"You are an expert in {tech_stack} programming. Answer this technical question: {question} , if the question falls outside of scope of programming and computer reply it with 'I can't respond to that, try asking something related to computer science.'"

    try:
        completion = client.chat.completions.create(
            model= model,
            messages=[
                {"role": "user", "content": "You are COMP-AI-LER, an expert system specialized in providing technical solutions for programming and computer science questions."},
                {"role": "user", "content": prompt}
            ]
        )
        print(completion.choices[0].message.content)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error getting response: {str(e)}"

#text callback for wrapping and fixing the textbox . -> default dearpygui dosent contain word wrap.
def text_callback(sender, app_data):
    # Get current text
    text = dpg.get_value(sender)
    input_width = dpg.get_item_width(sender)
    
    # Estimate character width based on font (approximate)
    char_width = 8  # Adjust this based on your font
    
    lines = text.split('\n')
    new_lines = []
    
    for line in lines:
        if len(line) * char_width > input_width:
            # Find wrap points
            current_line = ""
            words = line.split(' ')
            
            for word in words:
                test_line = current_line + word + ' '
                if len(test_line) * char_width > input_width:
                    new_lines.append(current_line)
                    current_line = word + ' '
                else:
                    current_line = test_line
            
            if current_line:
                new_lines.append(current_line)
        else:
            new_lines.append(line)
    
    # Set the wrapped text
    new_text = '\n'.join(new_lines)
    if new_text != text:
        dpg.set_value(sender, new_text)

#mouse drag callback to track and change window position -> default dearpygui dosent contain one.
#issue (mouse locks to some random values after focusing on input text)
def mouse_drag_callback(sender, app_data):
    """
    This callback is invoked when the left mouse button is dragged.
    app_data is a tuple (dx, dy) representing the drag delta.
    """
    if (dpg.is_item_focused("question_input")) or (dpg.is_item_focused("tech_input")):
        return 
    scroll , dx, dy = app_data  # Drag delta
    current_pos = dpg.get_viewport_pos()
    new_pos = (current_pos[0] + dx, current_pos[1] + dy)
    dpg.set_viewport_pos(new_pos)

#function to load logo image
def load_image(image_path):
    try:
        width, height, channels, data = dpg.load_image(image_path)
        with dpg.texture_registry():
            texture_id = dpg.add_static_texture(width, height, data)
        return texture_id, width, height
    except:
        return 0,0,0

#Copy Response Function To Copy The Generated Response
def copy_response():
    response_text = dpg.get_value("response_text")
    pyperclip.copy(response_text)
    dpg.set_value("copy_status", "Copied!")
    
    # Reset status after 2 seconds
    def reset_status():
        import time
        time.sleep(2)
        dpg.set_value("copy_status", "")
    
    threading.Thread(target=reset_status).start()

#final submit callback for sending request to LLM'S API
def submit_callback():
    question = dpg.get_value("question_input")
    tech_stack = dpg.get_value("tech_input")
    model = dpg.get_value("model_selector")

    if model == "":
        model = "gpt-4o-2024-05-13"
    if model == "gpt-4o":
        model = "gpt-4o-2024-05-13"
    if model == "claude-3.5-sonnet":
        model = "claude-3-5-sonnet"
    if model == "DeepSeek-R1":
        model = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
    if model == "deepseek-v3":
        model = "deepseek-v3"
    if model == "Meta-Llama":
        model = "Meta-Llama-3.3-70B-Instruct-Turbo"

    # Show loading message
    dpg.set_value("response_text", "Processing your request...")
    
    # Run AI query in a separate thread to prevent UI freezing
    def process_query():
        response = get_ai_response(question, tech_stack, model)
        dpg.set_value("response_text", response)
    
    threading.Thread(target=process_query).start()

#dearpygui create context and setup
dpg.create_context()
dpg.set_global_font_scale(1.15)#to change font size (1.0) default size
logo_texture, logo_width, logo_height = load_image("image.png") # Ensure the logo.png is in the same directory

#initilizing the handler to mouse drag on left click to keep track of window position
#with dpg.handler_registry():
    # The parameter 'button=0' indicates the left mouse button
    #dpg.add_mouse_drag_handler(button=0, callback=mouse_drag_callback)

#initilizing the primary window to create UI
with dpg.window(label="COMP-AI-LER", pos=(0, 0), width=600, height=580, no_focus_on_appearing=True,no_move=True, no_collapse=True, no_close=True, no_resize=True):
    
    #header and logo
    dpg.add_text("Welcome to COMP-AI-LER" , pos=(17, 42))
    dpg.add_image(logo_texture, tag="logo_image" , pos=(5, 50), width=200 , height=200)
    dpg.add_same_line()

    dpg.add_spacer(height=2)
    dpg.add_text("Models" , pos=(420,22))
    dpg.add_combo(pos=(420, 42),tag="model_selector" , items=Models, width=160)

    #question input box
    dpg.add_spacer(height=2)
    dpg.add_text("Your Question" , pos=(350,65))
    dpg.add_input_text(tag="question_input", multiline=True, pos=(220,88), height=100,width=360,callback=text_callback)
    dpg.add_same_line()

    #tech stack input box
    dpg.add_spacer(height=2)
    dpg.add_text("Tech Stack/Language" , pos=(330,187))
    dpg.add_input_text(tag="tech_input",multiline=True, pos=(220,209) ,height=50,width=360,callback=text_callback)
    dpg.add_same_line()
    dpg.add_spacer(height=2)

    # Submit button
    dpg.add_button(label="Ask AI", callback=submit_callback, width=200, height=30, pos=(300,270))
    dpg.add_spacer(height=12)

    # Copy Response Button
    dpg.add_text("Response:")
    dpg.add_button(label="Copy", tag="copy_status",callback=copy_response, width=100, height=25,pos=(85, 280))

    #Response Text
    dpg.add_separator()
    dpg.add_input_text(tag="response_text", multiline=True, callback=text_callback, readonly=True, width=582, height=240)

# Create a viewport without OS decorations (borderless, no title bar)
dpg.create_viewport(title="     ", width=616, height=600, small_icon="image.png", large_icon="image.png", resizable=False)#decorated=False

#setup dearpygui
dpg.setup_dearpygui()
dpg.show_viewport()

#render loop for rendering GUI
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

#destory GUI context and graphic buffers
dpg.destroy_context()
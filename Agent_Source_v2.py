#Initializing Search Tool and relevant variables
cost = 0
messageHistory = []
path_to_files = r'C:/Users/Hanson/AI_Agents/'

#Importing the necessary libraries
from urllib import response
from dotenv import dotenv_values
from tavily import TavilyClient
import base64
import os
import hashlib
from openai import OpenAI
from PIL import Image
import json
from termcolor import colored

# Load the environment variables from the .env file
env_vars = dotenv_values('.env')

# Retrieve the TEVILI_API_KEY
tavily_api_key = env_vars.get('TAVILY_API_KEY')

# Print the TEVILI_API_KEY
print(tavily_api_key)


tavily = TavilyClient(api_key=tavily_api_key)

def searchTavily(query):
    response = tavily.search(query)
    output = ''
    for result in response['results']:

        output += '---' + '\n'

        output += result['title'] + '\n'

        output += result['url'] + '\n'

        output += result['content'] + '\n'

        output += '---' + '\n'
    return output



#Example of the structure of a tools query in JSON format 
'''tools = [
  {
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
          },
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
      },
    }
  }
]'''

#defines search function JSON query structure 
search_function = {
    "type": "function",
    "function": {
        "name": "searchTavily",
        "description": "Search the internet for results based on a query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                'thought': {
                    'type': 'string',
                    'description': 'The thought that made you use this tool'
                }
            },
            "required": ["query"]
        }
    }
}

#defines image generation JSON query structure
generate_image = {
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Customer service agent to generate an image based on a query. provide it with all necessary details to generate an image. Every query will be a new agent responding.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The image query"
                }
            },
            "required": ["query"]
        }
    }
}

def hash_string(string):

    # Create a hash object
    hash_object = hashlib.sha256()

    # Convert the string to bytes and hash it
    hash_object.update(string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_string = hash_object.hexdigest()

    return hashed_string



#defines the image generation API Call that returns file path to generated image
def generateImage(query):
    client = OpenAI()
    print('prompt: ', query)
    print('generating image...')
    image = client.images.generate(
        model="dall-e-3",
        prompt=query,
        n=1,
        size="1024x1024",
        response_format='b64_json'
    )
    
    imgdata = base64.b64decode(image.data[0].b64_json)

    # FILEPATH: /c:/Users/Hanson/AI_Agents/agent_Source.ipynb
    filename = f'{path_to_files}{hash_string(image.data[0].revised_prompt)}'+'.jpg'  # I assume you have a way of picking unique filenames

    if not os.path.exists(filename):
        with open(filename, 'wb') as f:
            f.write(imgdata)

    im = Image.open(f"{filename}")
    # This method will show image in any image viewer  
    im.show()  
    global cost
    cost += 0.040
    return filename

#tools for asking user for more information
ask_user = {
    "type": "function",
    "function": {
        "name": "askUser",
        "description": "Ask the user for more information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to ask the user"
                }
            },
            "required": ["query"]
        }
    }
}

#defines the ask_user tool
def askUser(query):
    print(query)
    user_response = input("Enter your response: ")
    return 'Query: '+query+'\nUser Response: '+ user_response




#defines image generation agent
def imageAgent(query):
    client = OpenAI()
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[{"role": "system", "content": '''You will generate a description of an image, and from the image description prompt, an AI image creator software product will produce the image. As it is easy for a user to overlook the required specifications, be sure that you’ve received almost all of these criteria from user instruction or earlier chat:
            purpose
            medium - photo, painting, graphic art, 3d simulation, …
            style
            subject
            subject pose or action
            setting
            background imagery
            more possibilities: mood, tone, time of day
            These can be specifications you write and apply to create a satisfying image prompt. They also can be criteria where instead of writing the image prompt, you ask the user for more information if user instructions are not clear. always ask in the form of: "can you provide more information about ____ when rewriting your next query for the next agent? "
            You have to choose from 2 options: 
            1. Ask the user for more information
            2. Produce the Image using the Tool provided
            If you have questions to ask the user, you must ask them in  JSON format. 
            If you choose to produce the Image, you must provide the query in JSON format.
                   
            The prompt should be objective, explicit, and comprehensive. Do not use vague or ambiguous language.
            '''},
            {"role": 'user', "content": query}],
        tools = [ask_user, generate_image], 
        temperature = 0
    )
    response_message = completion.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "ask_user": askUser,'generate_image': generateImage
        }
        responses = []
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_name == "ask_user":
                function_response = function_to_call(
                    query=function_args.get("query")
                )
                function_response += "Here is the response from the user: " + function_response
            elif function_name == "generate_image":
                function_response = function_to_call(
                    query=function_args.get("query")
                )
                function_response += "Here is the filepath to the image you requested: " + function_response
                
            responses.append(function_response)
    else:
        raise Exception("No tool calls were made by the imageAgent", completion)
    response = completion
    global cost
    cost += response.usage.prompt_tokens * GPT3_input_cost + response.usage.completion_tokens * GPT3_output_cost
    return responses

#tools JSON query structure for imageAgent: 
image_Agent = {
    "type": "function",
    "function": {
      "name": "imageAgent",
      "description": '''Generate an image based on a detailed query including purpose
            medium - photo, painting, graphic art, 3d simulation, …
            style
            subject
            subject pose or action
            setting
            background imagery
            more possibilities: mood, tone, time of day''',
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The image query"
          }
        },
        "required": ["query"]
      }
    }
  }



#text agent

def textAgent(query, messageHistory=messageHistory):
  from openai import OpenAI
  import os

  client = OpenAI()
  messages=[
          {"role": "system", "content": "You are now the Text Agent instead. Your task is to produce text based on the given query. You do not have access to the tools mentioned. You simply procude waht is demanded by the query. The generated text should be fo High Quality and in MarkDown forma. Never include suggestions. Only the Body of text is required."},
          {"role": "user", "content": query}
      ]
  messages = messageHistory + messages
  
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=messages,
    temperature = 0
  )

  response_message = completion.choices[0].message
  action = response_message.content

  # Save the generated string in Markdown format
  markdown_string = action
  filename = f"{path_to_files}/{hash_string(markdown_string)}.md"
  print(f"Saving the generated text to {filename}")

  with open(filename, "w") as file:
    file.write(markdown_string)
  response = completion
  global cost
  cost += response.usage.prompt_tokens * GPT3_input_cost + response.usage.completion_tokens * GPT3_output_cost
  # Open the file
  os.startfile(filename)

  return action

#tools JSON query structure for actionAgent:
text_Agent = {
    "type": "function",
    "function": {
      "name": "textAgent",
      "description": "Produces text, such as stories, articles, and more, based on a given query. The agent does not have access to the tools mentioned in the query. The query should include metadata about the text, such as the purpose, style, tone and length, language style, and structure. Never ask it to make suggestions. ",
      "parameters": {
        "type": "object",
        "properties": {
          "query": {
            "type": "string",
            "description": "The query"
          }
        },
        "required": ["query"]
      }
    }
  }


#tools JSON query structure for Thoughts function
output_Thoughts = {
    "type": "function",
    "function": {
        "name": "outputThoughts",
        "description": "Place to output your thoughts for the actions you think you will take to fufill the request",
        "parameters": {
            "type": "object",
            "properties": {
                "thought": {
                    "type": "string",
                    "description": "Your thought on what the next step of action should be and why", 
                'action': {
                    'type': 'string',
                    'description': 'Description and explaination of the action you think you will take'
                },
                'final': {
                    'type': 'boolean',
                    'description': 'Whether you think you have fufilled the request or not'
                }}
            },
            "required": ["thought", "action", 'final']
        }
    }
}




#main agent initialization

client = OpenAI()
cost = 0
GPT4_input_cost = 30/1000000
GPT4_output_cost = 60/1000000
GPT3_input_cost = 0.5/1000000
GPT3_output_cost = 1.5/1000000
#defining the main AI agent Iterations
def chatIteration( tools, messageHistory, user='user',message = ''):
    if message != '':
        messageHistory.append({"role": user, "content": message})
    response = client.chat.completions.create(
        response_format={ "type": "json_object" },
        model="gpt-4-turbo",
        messages=messageHistory,
        temperature = 0,
        tools = tools
    )    
    global cost
    cost += response.usage.prompt_tokens * GPT4_input_cost + response.usage.completion_tokens * GPT4_output_cost
    return response.choices[0].message
#system prompt that will be sent to the API every iteration
system_message = 'You are Carbon Linking AI agent, an AI agent designed by the company Carbon Linking. \nCarbon Linking is a Hong Kong based green tech company that is redefining carbon literacy delivery and green actions through technology and play. \nYou are responsible for helping out the employees of Carbon Linking to solve problems.\nYou should be independent in solving problems and creative in answering requests.\n\nAnswer the following requests as best you can. You have access to the following tools:\n\n{tools}\nThese tools can only accessed through JSON.\n\nWhen you respond to a message, you must respond using the following JSON format using the tool:\nrequest: the input request you must fufil\nThought: you should always think about what to do\nAction: A description fo the action you wish to take and why. This includes Using a tool.\n(this Thought/Action can repeat infinite times until you DEFINITELY have EXACTLY fufilled the request.)\n Try not to repeat the actions of what you have done before.\n\nIf you are done, Output the \'Final\' variable as \'True\' to end your job. \n\nYour response must be on of the following: \n1. [Only using the OutputThought tool]\n2. [Using the OutputThought tool + another tool]\n*Under all circumstances you are mandated to use the OutputThought tool*\nCompile your Final answer the the request as a \'thought\' tool.\n\nBegin!\n\nRequest: {initial_prompt}.'


messageHistory = []
tools = [search_function, image_Agent, ask_user,text_Agent, output_Thoughts] #add the JSON format of the tool.
initial_prompt = r'Write an article to illustrate the importance of tracking carbon footprints. Use statistics in your article. Finally, after you\'re done, generate an image to accompany the article. This will be posted on the carbon linking blog.' #can be changed to GUI input

response = chatIteration(message = system_message.format(tools = str(tools), initial_prompt=initial_prompt), tools=tools, messageHistory=messageHistory, user='system')
print(response)



cost

  
def pretty_print_conversation(message):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    if message["role"] == "system":
        print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
    elif message["role"] == "user":
        print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
    elif message["role"] == "assistant" and message.get("function_call"):
        print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
    elif message["role"] == "assistant" and not message.get("function_call"):
        print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
    elif message["role"] == "function":
        print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))



pretty_print_conversation(messageHistory[-1])
End = 0

debug = []
while End != 2: 
    #step 1: append model message to messageHistory
    
    tool_calls = response.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "askUser": askUser,'imageAgent': imageAgent, 'searchTavily': searchTavily, 'outputThoughts': 'outputThoughts', 'textAgent': textAgent
        }
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            print('Function Called: ' + function_name)
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            if function_name == "outputThoughts":
                thought = function_args.get("thought")
                action = function_args.get("action")
                final = function_args.get("final")
                if final == True:
                    End +=1               
                messageAppend = {'role':'assistant', 'content':f'Thought: {thought}\nAction: {action}\nFinal: {final}'}
            else:
                query = function_args.get("query")
                function_response = function_to_call(query=query)
                messageAppend = {'role':'system', 'content':f'Tool name: {function_name}\nTool Input: {query}\nTool Output: {function_response}'}

            messageHistory.append(messageAppend)
            pretty_print_conversation(messageHistory[-1])
    elif response.content != None:
        try:
            dict_response = json.loads(response.content)
            thought = dict_response['thought']
            action = dict_response['action']
            final = dict_response['final']
        except:
            messageAppend = {'role':'system', 'content':'Exception: Agent Thought detected in direct message. Please use the OutputThoughts tool to output your thoughts.'}
            messageHistory.append(messageAppend)
            pretty_print_conversation(messageHistory[-1])
            print(response.content)
        else: 
            messageAppend = {'role':'assistant', 'content':f'Thought: {thought}\nAction: {action}\nFinal: {final}'}
            pretty_print_conversation(messageHistory[-1])
            if final == True:
                print('Agent has attempted to end Conversation. Executing final confirmation sequence...')
                End +=1               
                messageAppend = {'role':'User', 'content':f'Are you sure you have fufilled the request? Are you sure I will see the final product? '}
                messageHistory.append(messageAppend)
                pretty_print_conversation(messageHistory[-1])
    if End == True:
        break
    else: 
        response = chatIteration(tools=tools, messageHistory=messageHistory)
        debug.append(response)
    


print(str(round(cost*7.84,2)) + ' HKD')


 '''
for i in messageHistory:
    pretty_print_conversation(i)


response.content.get['thought']


response.content
'''


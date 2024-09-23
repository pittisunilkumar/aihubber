import os
import logging
from flask import Flask, request, render_template, jsonify
from groq import Groq
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
import markdown

app = Flask(__name__)

# Groq API setup
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

# Gemini API setup
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "AIzaSyDjNoWvxh6JV-mNBF148_zDKAT8PbyvpjI")
genai.configure(api_key=GOOGLE_API_KEY)

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def query_groq_model(model_name, input_text):
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": input_text}],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.65,
            stream=True,
            stop=None,
        )

        generated_text = ""
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                generated_text += chunk.choices[0].delta.content
        return generated_text
    except Exception as e:
        logging.error(f"Error querying {model_name} API: {e}")
        return f"Error: Unable to generate response from {model_name}. {str(e)}"

def query_groq_llama(input_text):
    return query_groq_model("llama3-groq-8b-8192-tool-use-preview", input_text)

def query_mixtral(input_text):
    return query_groq_model("mixtral-8x7b-32768", input_text)

def query_gemma(input_text):
    return query_groq_model("gemma2-9b-it", input_text)

def get_gemini_generation(input_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        logging.error(f"Error querying Gemini API: {e}")
        return f"Error: Unable to generate response from Gemini. {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('input_text', '').strip()
        if input_text:
            try:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {
                        executor.submit(query_groq_llama, input_text): "groq_llama",
                        executor.submit(query_mixtral, input_text): "mixtral",
                        executor.submit(query_gemma, input_text): "gemma",
                        executor.submit(get_gemini_generation, input_text): "gemini"
                    }

                    results = {}
                    for future in as_completed(futures):
                        model = futures[future]
                        try:
                            results[model] = markdown.markdown(future.result())
                        except Exception as e:
                            results[model] = f"Error: {str(e)}"

                return render_template('index.html',
                                       groq_llama_output=results.get("groq_llama", ""),
                                       mixtral_output=results.get("mixtral", ""),
                                       gemma_output=results.get("gemma", ""),
                                       gemini_output=results.get("gemini", ""))
            except Exception as e:
                return render_template('index.html', error=f"An error occurred: {str(e)}")
        else:
            return render_template('index.html', error="Please enter a prompt.")

    return render_template('index.html',
                           groq_llama_output="",
                           mixtral_output="",
                           gemma_output="",
                           gemini_output="")

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask,request,render_template,jsonify,url_for
import os,sys,requests,json
from random import randint
from flask_mysqldb import MySQL
import MySQLdb.cursors
import yaml
from flask_socketio import SocketIO, emit

app=Flask(__name__)
mysql = MySQL(app)
# socketio = SocketIO(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'hpcl'
app.config['MYSQL_PORT'] = 3309
app.config['MYSQL_CURSORCLASS'] = "DictCursor"

def read_yaml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
@app.route('/delete')
def delete():
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM messages")
    mysql.connection.commit()
    cur.close()
    return jsonify({"status": "success"})

@app.route('/db', methods=['GET'])
def db():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM messages WHERE displayed=0")
    messages = cur.fetchall()
    response_data = []
    for msg in messages:
        response_data.append({
            'id': msg['id'],
            'messages': msg['message'],
            'buttons': json.loads(msg['buttons']) if msg['buttons'] else []
        })
        cur.execute("UPDATE messages SET displayed=1 WHERE id=%s", (msg['id'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({"response": response_data})

@app.route('/callback', methods=['POST'])
def rasa_callback():
    data = request.json
    cur = mysql.connection.cursor()
    buttons = json.dumps(data.get('buttons', []))  # Convert buttons to JSON string
    cur.execute("INSERT INTO messages (message, buttons) VALUES (%s, %s)", (data['text'], buttons))
    mysql.connection.commit()
    cur.close()
    return jsonify({"status": "success"})

@app.route('/get', methods=['GET','POST'])
def get_bot_response():
    userText = str(request.args.get('msg'))
    data = json.dumps({"sender": "312", "message": userText})
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    # try:
    response = requests.request("POST",   url="http://localhost:5005/webhooks/callback/webhook", headers=headers, data=data)
    # print(response)
    # response_json = response.json()
    # if response_json and len(response_json) > 0:
    # return str(response_json['text'])
    #     else:
    #         return "Sorry, I couldn't process that request."
    # except requests.exceptions.RequestException as e:
    #     print(f"Error communicating with Rasa server: {e}")
    #     return "Sorry, there was an error processing your request."
    return jsonify({"status": "success"})

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/page',methods=['GET','POST'])
def page():
    return render_template('page.html')

@app.route('/add',methods=['GET','POST'])
def add():
    return render_template('add.html')

@app.route('/edit',methods=['GET','POST'])
def edit():
    response=str(request.args.get('response'))
    intent=str(request.args.get('intent'))
    with open(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\nlu.yml', 'a') as file:
        file.write("\n- intent: "+intent)
    examples=str(request.args.get('examples'))
    a = examples.split('\n')
    examples = "\n    - ".join([str(item) for item in a])
    with open(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\nlu.yml', 'a') as file:
        file.write("\n  examples: |\n    - "+examples)
    file = open(r'C:\Users\admin\Desktop\VS Code\rasa_new\domain.yml', "r+")
    temp = file.read()
    pos = temp.find("intents:") + len("intents:") + 1
    file.seek(pos, 0)
    data = file.read()
    intent_statement = "\n- "+ intent
    file.seek(pos, 0)
    file.write(intent_statement)
    file.write(data)
    file.close()
    #//////////////////
    
    domain_path = r'C:\Users\admin\Desktop\VS Code\rasa_new\domain.yml'
    with open(domain_path, 'r') as file:
        lines = file.readlines()
    
    responses_index = -1
    for i, line in enumerate(lines):
        if line.strip() == 'responses:':
            responses_index = i
            break
    
    if responses_index != -1:
        new_response = f"  utter_{intent}:\n  - text: {response}\n"
        lines.insert(responses_index + 1, new_response)

        with open(domain_path, 'w') as file:
            file.writelines(lines)
    
    with open(domain_path, 'r') as file:
        lines = file.readlines()
    
    responses_index = -1
    for i, line in enumerate(lines):
        if line.strip() == 'actions:':
            responses_index = i
            break
    
    if responses_index != -1:
        new_response = f"- utter_{intent}\n"
        lines.insert(responses_index + 1, new_response)
 
        with open(domain_path, 'w') as file:
            file.writelines(lines)

    with open(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\rules.yml', 'a') as file:
        file.write("\n- rule: "+response+"\n  steps:\n  - intent: "+intent+"\n  - action: utter_"+intent)

    training_data = {
    "config": read_yaml_file(r'C:\Users\admin\Desktop\VS Code\rasa_new\config.yml'),
    # "nlu": read_yaml_file(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\nlu.yml'),
    "domain": read_yaml_file(r'C:\Users\admin\Desktop\VS Code\rasa_new\domain.yml'),
    "stories": read_yaml_file(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\stories.yml'),
    "rules": read_yaml_file(r'C:\Users\admin\Desktop\VS Code\rasa_new\data\rules.yml')
}
    yaml_data = yaml.dump(training_data, default_flow_style=True)
    print(yaml_data)
    try:
        response = requests.post("http://localhost:5005/model/train", data=yaml_data, headers={"Content-Type": "application/yaml"})
        response.raise_for_status()
        return jsonify({"status": "success"})
    except requests.exceptions.RequestException as e:
        return jsonify({"status": "error", "message": str(e)})
    # return render_template('add.html')

# if __name__ == '__main__':
#     socketio.run(app)
    
if (__name__)=="__main__":
    app.run(debug=True, port=5000)

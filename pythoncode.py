from flask import Flask, Response, render_template, request
import webbrowser

app = Flask(__name__)

# methods = post means it expects to receive something
# get means its asking for something
@app.route('/myFunc', methods=['POST'])
def myFunc():
	input = request.files['file']
	#do stuff
	#csv = input
	csv = '1,2,3\n4,5,6\n' #put csv file here
	return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=fileName.csv"})



@app.route('/')
def webpage():
	return render_template('index.html')

if __name__ == '__main__':
	webbrowser.open('http://127.0.0.1:5000/', new=2)
	app.run()
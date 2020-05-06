from flask import Flask, Response, render_template
import webbrowser

app = Flask(__name__)

@app.route('/myFunc', methods=['POST'])
def myFunc():
	
	#do stuff
	
	csv = '1,2,3\n4,5,6\n' #put csv file hear
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
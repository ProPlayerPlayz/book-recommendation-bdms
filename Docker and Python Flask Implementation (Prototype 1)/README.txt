Note: You will need docker installed and Docker Engine Running to use the program via Docker
      If you don't have Docker please follow the alternate instructions

-------------------------------------------------------------------------------------------
To Run the program via Docker,

1) Open a Terminal in this Directory
2) Run "docker compose up"
3) With the terminal still running open a browser and open "localhost:5000" to view the Python Flask Webpage
4) When done, you can press Ctrl+C to stop the docker containers
5) To uninstall and remove the images created you can run "docker compose down"
6) To also delete the database created within docker volumes you can run "docker compose down --volumes"

-------------------------------------------------------------------------------------------

-------------------------------------------------------------------------------------------
To Run the program without Docker,

1) open "app.py" in any code/text editor of your choice
2) Uncomment Line 26 containing the following data:
	Line 26 -> app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/prolib'
3) Save the file and close it
4) Run app.py via your native python installation
5) With the program running, open your browser and go to "localhost:5000" to view the Python Flask Webpage
6) You can stop the program by pressing Ctrl+C

-------------------------------------------------------------------------------------------


===========================================================================================

To Reset the database and generate brand new fake data,
Run the 'fake_data_gen.py' file using your native python installation
and reopen the WebUI to see the changes

===========================================================================================

Also note that all codes within this implementation has comments for easy readability
If any problem occuers refer to the code files directly and the comments should be
able to clear up the issue by pointing to lines that you may need to comment out or uncomment

===========================================================================================




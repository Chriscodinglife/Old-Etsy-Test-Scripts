/*
  /$$$$$$  /$$                 /$$          
 /$$__  $$| $$                |__/          
| $$  \__/| $$$$$$$   /$$$$$$  /$$  /$$$$$$$
| $$      | $$__  $$ /$$__  $$| $$ /$$_____/
| $$      | $$  \ $$| $$  \__/| $$|  $$$$$$ 
| $$    $$| $$  | $$| $$      | $$ \____  $$
|  $$$$$$/| $$  | $$| $$      | $$ /$$$$$$$/
 \______/ |__/  |__/|__/      |__/|_______/ 
               
                       
Christian Orellana
January 2022
Create Twitch After Effects Compositions Template Automation

:: About This ::
This is a master template for automating the After Effects Creation of Twitch Overlay 
Compositions. This is written in Javascript XML for After Effects 

References:
| After Effects Automate with CSV Files | https://www.youtube.com/watch?v=UKdM56livIY |
| Extend Script Java Docs | https://extendscript.docsforadobe.dev/ |
| After Effects Scripting Guide | https://ae-scripting.docsforadobe.dev/
*/

var csvData = [];


// Create basic log function | Courtesy to https://community.adobe.com/t5/illustrator-discussions/how-to-log-the-extendscript-tool-kit-console-prints-to-a-text-file/td-p/7313061
function logMe(input){

  var now = new Date();
  var output = now.toTimeString() + ": " + input;
  $.writeln(output);
  var logFile = File("log.txt");
  logFile.open("e");
  logFile.writeln(output);
  logFile.close();

}


// Load in the CSV File for reading what comps need to be created
function loadCSV() {

  var csvFile = File("twitch_stream_template.csv");
  
  csvFile.open("r");
  do {
      csvData.push(csvFile.readln());
      } while(!csvFile.eof);

  csvFile.close();
}


// Use this generic function to create comps when the function is called and return them
function createComp(name, width, height) {

  var pixelAspect = 1; // 1 to 1 pixel Aspect Ration
  var duration = 10; // Seconds
  var frameRate = 60; // FPS
  var myComp = app.project.items.addComp(name, width, height, pixelAspect, duration, frameRate)
  return myComp;
}


// Use this function to quickly create folders and return them
function createFolder(name) {

  var folder = app.project.items.addFolder(name);
  return folder;
}


// Get the Folder object for the specified Folder by name
function getFolder(folderName) {

  for (var i = 1; i <= app.project.numItems; i++) {
    if (app.project.item(i).name == folderName && app.project.item(i) instanceof FolderItem){
      return app.project.item(i);
    }
  }
}


// Get the Comp Item Object based on the name of the Comp
function getComp(compName) {

  for (var i = 1; i <= app.project.numItems; i++) {
    if (app.project.item(i).name == compName && app.project.item(i) instanceof CompItem) {
      return app.project.item(i);
    }
  }
}


// Setup the Template Project in After Effects
function masterSetup() {

  // Create a Master Folder
  var masterFolder = createFolder("Comps");
  masterFolder = getFolder("Comps");

  // Iterate through the CSV data and start creating compositions
  var thisCSVRow, myComp, theseTypes;
  for (var i = 1; i < csvData.length; i++) {

    // Register each row into a single row
    thisCSVRow = csvData[i].split(",");
    
    // Create a Folder for each Row
    var subFolder = createFolder(thisCSVRow[0]);
    subFolder = getFolder(thisCSVRow[0]);

    // Check if the Row's Type is set to None. If it is Make the Row's Comp as standalone
    // Anything Else, it will create all the specified comps listed in Types
    if (thisCSVRow[3] == "None") {
      var nameOfComp;
      nameOfComp = thisCSVRow[0].concat("_", thisCSVRow[1], "_", thisCSVRow[2]);
      myComp = createComp(nameOfComp, parseInt(thisCSVRow[1]), parseInt(thisCSVRow[2]));
      myComp = getComp(nameOfComp);
      myComp.parentFolder = subFolder;
    } else {
      theseTypes = thisCSVRow[3].slice(1, thisCSVRow[3].length-1).split("|");
      for (var type = 0; type < theseTypes.length; type++) {
        var nameOfComp;
        nameOfComp = theseTypes[type].concat("_", thisCSVRow[0], "_", thisCSVRow[1], "_", thisCSVRow[2]);
        myComp = createComp(nameOfComp, parseInt(thisCSVRow[1]), parseInt(thisCSVRow[2]));
        myComp = getComp(nameOfComp);
        myComp.parentFolder = subFolder;
      }
    }
    subFolder.parentFolder = masterFolder;
  }
}


loadCSV();
masterSetup();
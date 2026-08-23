  //const folderId = "18ApP2GbqGe3BBghjnqcU2WBDykJ3rRyB"; // Replace with your main folder's ID
  const sheetName = "canti"; // Replace with your Google Sheet tab name
  const sheetId = "1hIOOv7dQ1rHjhVGQii8RksQlKpRjXs8_-CIrnKj97Yo"

function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('Index')
      .setSandboxMode(HtmlService.SandboxMode.IFRAME)
      .setTitle('Divina Commedia')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);//.addMetaTag('Content-Language', 'en');
}

function getData(sheetName="canti") {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sheet) throw new Error(`Sheet "${sheetName}" not found.`);

  const data = sheet.getDataRange().getValues();

  const result = [];
  for (let i = 1; i < data.length; i++) { // Skip the header row
    const [name1, name2, name3, name4, name5] = data[i].slice(0, 5);
    const links = [];

    result.push({
      name: name4,
      x: data[i][8], // Column O (index 14)
      y: data[i][9], // Column P (index 15)
      z: data[i][10], // Column Q (index 16)
      x2d: data[i][6],
      y2d: data[i][7],
      size: 3, // Column A (index 0)
      color: data[i][0], // Column N (index 18)
      text: data[i][2],
      cantica: data[i][0],
      canto: data[i][1]
    });
  }
  return result;
}

function getTercetData(sheetName="terzine") {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sheet) throw new Error(`Sheet "${sheetName}" not found.`);

  const data = sheet.getDataRange().getValues();

  const result = {};
  for (let i = 1; i < data.length; i++) { // Skip the header row
    const [cantica, canto, terzina, text, label, topic, sentiment, score] = data[i].slice(0, 8);
    if(!(cantica in result)){
      result[cantica]={};
    }
    var aiddict=result[cantica];
    if(!(canto in aiddict)){
      aiddict[canto]=[];
    }
    aiddict[canto].push([terzina, text, sentiment, score]);
  }
  return result;
}

function getSheetData() {
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  const dataRange = sheet.getDataRange();
  const richTextValues = dataRange.getRichTextValues(); // Retrieve rich text values
  const plainValues = dataRange.getValues(); // Retrieve plain cell values for non-hyperlink data

  // Iterate through rows and extract hyperlink addresses
  const data = plainValues.map((row, rowIndex) => {
    return row.map((cell, colIndex) => {
      const richTextValue = richTextValues[rowIndex][colIndex];
      const link = richTextValue ? richTextValue.getLinkUrl() : null; // Get hyperlink URL if available
      return link || cell; // Use URL if it exists, otherwise plain text
    });
  });

  return data;
}

function saveClassification(row, classification, sheetId, sheetName) {
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  sheet.getRange(row, 7).setValue(classification); // Save classification in column 7
}

function logError(row, errorMessage, sheetId, sheetName) {
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  sheet.getRange(row, 8).setValue(errorMessage); // Save error in column 8
}

function saveAllClusters(rowIndices, clusters) {
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  for (let i = 0; i < rowIndices.length; i++) {
    sheet.getRange(rowIndices[i], 13).setValue(clusters[i]); // Save clusters in column M
  }
}

function getFirstEmptyRowEfficient() {
  const sheet = SpreadsheetApp.openById(sheetId).getSheetByName(sheetName);
  const columnValues = sheet.getRange("A:A").getValues(); // Get all values in column A
  for (let i = 0; i < columnValues.length; i++) {
    if (!columnValues[i][0]) {
      return i + 1; // Rows are 1-based in Google Sheets
    }
  }
  return columnValues.length + 1; // All rows filled, so return next row
}

function generateProblemsDoc(year = -1, level = 2, type = 'problema', group = [0,1,2,3]) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ['1livello', '2livello'];
  const doc = DocumentApp.create(
    `Problems for Group ${Array.isArray(group) ? group.join(', ') : group} - ${Array.isArray(year) ? year.join(', ') : (year === -1 ? 'All Years' : year)} ${Array.isArray(level) ? level.join(', ') : (level === -1 ? 'All Levels' : level)} ${Array.isArray(type) ? type.join(', ') : (type === -1 ? 'All Types' : type)}`
  );
  const body = doc.getBody();

  sheets.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;
    const maxImageWidth = 650;
    const data = sheet.getDataRange().getValues();
    const richTextData = sheet.getDataRange().getRichTextValues(); // Get rich text values to extract hyperlinks

    // Hardcoded column indices
    const yearIndex = 0; // Column A
    const levelIndex = 2; // Column C
    const typeIndex = 3; // Column D
    const numberIndex = 4; // Column E
    const groupIndex = 13; // Column N
    const linkColumns = [5, 6, 7]; // Columns F, G, H

    // Iterate over rows
    for (let i = 0; i < data.length; i++) { // No headers, start from row 0
      const row = data[i];
      const rowYear = row[yearIndex];
      const rowLevel = row[levelIndex];
      const rowType = row[typeIndex];
      const rowNumber = row[numberIndex];
      const rowGroup = row[groupIndex];

      // Apply filters (skip entries that do not match, unless filter is -1)
      if (
        (year !== -1 && (!Array.isArray(year) ? rowYear !== year : !year.includes(rowYear))) ||
        (level !== -1 && (!Array.isArray(level) ? rowLevel !== level : !level.includes(rowLevel))) ||
        (type !== -1 && (!Array.isArray(type) ? rowType !== type : !type.includes(rowType))) ||
        (group !== -1 && (!Array.isArray(group) ? rowGroup !== group : !group.includes(rowGroup)))
      ) {
        continue; // Skip this row if it doesn't match
      }

      // Add problem details
      body.appendHorizontalRule();
      body.appendParagraph(`Year: ${rowYear}; ` + `Level: ${rowLevel}`);
      body.appendParagraph(`Type: ${rowType}; ` + `Problem Number: ${rowNumber}`);

      // Add images from hyperlinks
      linkColumns.forEach(colIndex => {
        const richText = richTextData[i][colIndex]; // Access rich text value
        if (richText) {
          const link = richText.getLinkUrl(); // Get the hyperlink URL
          if (link) {
            try {
              const fileId = link.match(/[-\w]{25,}/)[0]; // Extract file ID from link
              const file = DriveApp.getFileById(fileId);
              const blob = file.getBlob();
              const image = body.appendImage(blob);

              let width = image.getWidth();
              let height = image.getHeight();

              // Resize image to fit the document width
              image.setWidth(maxImageWidth);
              image.setHeight((height * maxImageWidth) / width);
            } catch (e) {
              Logger.log(`Error adding image for link ${link}: ${e.message}`);
            }
          }
        }
      });

      body.appendParagraph('\n'); // Add spacing between problems
    }
  });

  doc.saveAndClose();
  return doc.getUrl();
}

function generateQuizForm(year = [2015,2016], level = 1, type = 'quesito', group = 5) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ['1livello', '2livello'];
  const form = FormApp.create(`Quiz for Group ${Array.isArray(group) ? group.join(', ') : group} - ${Array.isArray(year) ? year.join(', ') : (year == -1 ? 'All Years' : year)} ${Array.isArray(level) ? level.join(', ') : (level == -1 ? 'All Levels' : level)} ${Array.isArray(type) ? type.join(', ') : (type == -1 ? 'All Types' : type)}`);
  // Enable Quiz settings
  form.setIsQuiz(true);
  form.setAllowResponseEdits(false);
  form.setCollectEmail(true)

  sheets.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;

    const data = sheet.getDataRange().getValues();
    const richTextData = sheet.getDataRange().getRichTextValues();

    // Hardcoded column indices
    const yearIndex = 0; // Column A
    const levelIndex = 2; // Column C
    const typeIndex = 3; // Column D
    const numberIndex = 4; // Column E
    const groupIndex = 13; // Column N
    const answerColumnIndex = 25; // Column Z (zero-based)
    const linkColumns = [5, 6, 7]; // Columns F, G, H

    for (let i = 0; i < data.length; i++) {
      const row = data[i];
      const rowYear = row[yearIndex];
      const rowLevel = row[levelIndex];
      const rowType = row[typeIndex];
      const rowNumber = row[numberIndex];
      const rowGroup = row[groupIndex];
      const correctAnswer = row[answerColumnIndex]; // The correct answer (A, B, C, D, E)

      // Apply filters
      if ((year !== -1 && (!Array.isArray(year) ? rowYear !== year : !year.includes(rowYear))) ||
          (level !== -1 && (!Array.isArray(level) ? rowLevel !== level : !level.includes(rowLevel))) ||
          (type !== -1 && (!Array.isArray(type) ? rowType !== type : !type.includes(rowType))) ||
          (group !== -1 && (!Array.isArray(group) ? rowGroup !== group : !group.includes(rowGroup)))) {
        continue;
      }

      // Add images from hyperlinks
      let imageAdded = false;
      linkColumns.forEach(colIndex => {
        const richText = richTextData[i][colIndex];
        if (richText) {
          const link = richText.getLinkUrl();
          if (link) {
            try {
              const fileId = link.match(/[-\w]{25,}/)[0];
              const file = DriveApp.getFileById(fileId);
              const blob = file.getBlob();
              form.addImageItem().setTitle(`Year: ${rowYear}, Level: ${rowLevel}, Type: ${rowType}, Problem Number: ${rowNumber}`).setImage(blob); // Add image above the question
              imageAdded = true;
            } catch (e) {
              Logger.log(`Error adding image for link ${link}: ${e.message}`);
            }
          }
        }
      });

      // Create a new question in the form
      const item = form.addMultipleChoiceItem();
      item.setTitle(`Risposta`);

      // Set the choices for the question
      const choices = ['A', 'B', 'C', 'D', 'E'].map(choice => {
        if (choice === correctAnswer) {
          return item.createChoice(choice, true);
        }
        return item.createChoice(choice, false);
      });

      item.setChoices(choices);
      item.setPoints(5); // Points for correct answer
      item.setRequired(true); // Make the question mandatory
    }
  });

  // Configure the quiz grading settings
  form.setLimitOneResponsePerUser(true);

  return form.getEditUrl();
}

function generateQuiz(data) {
  const years = data.years;
  const groups = data.groups;

  if (!years || !groups) {
    throw new Error('Years and Groups must be provided.');
  }

  const yearArray = years.split(',').map(y => parseInt(y.trim()));
  const groupArray = groups.split(',').map(g => parseInt(g.trim(), 10));

  const quizUrl = generateQuizForm(yearArray, 1, 'quesito', groupArray);
  return quizUrl;
}

function getGroupLabels() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('groups');
  if (!sheet) throw new Error('Sheet "groups" not found.');

  const data = sheet.getDataRange().getValues();

  const groupLabels = data.map(row => {
    return {
      number: row[0],
      label: row[1]
    };
  }).filter(group => (group.number>=0) && group.label); // Ensure valid entries

  return groupLabels;
}

function getAvailableYearsAndGroups() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('1livello');
  if (!sheet) throw new Error('Sheet "1livello" not found.');

  const data = sheet.getDataRange().getValues();

  const yearIndex = 0; // Column A
  const groupIndex = 13; // Column N

  const years = new Set();
  const groups = new Set();

  data.forEach(row => {
    years.add(row[yearIndex]);
    groups.add(row[groupIndex]);
  });

  return {
    years: Array.from(years).filter(Boolean).sort(),
    groups: Array.from(groups).filter(Boolean).sort((a, b) => a - b)
  };
}

function generateQuizFromPoints(points) {
  /**
   * Points: List of tuples, each tuple includes
   * [year, type, category, exercise number].
   */
  Logger.log(points);
  if (!points || points.length === 0) {
    throw new Error("No points provided to generate the quiz.");
  }
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheets = ['1livello', '2livello'];
  const form = FormApp.create(`Custom Quiz`);

  // Enable Quiz settings
  form.setIsQuiz(true);
  form.setAllowResponseEdits(false);
  form.setCollectEmail(true);

  sheets.forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) return;

    const data = sheet.getDataRange().getValues();
    const richTextData = sheet.getDataRange().getRichTextValues();

    // Hardcoded column indices
    const yearIndex = 0; // Column A
    const typeIndex = 1; // Column B
    const categoryIndex = 3; // Column D
    const numberIndex = 4; // Column E
    const answerColumnIndex = 25; // Column Z (zero-based)
    const linkColumns = [5, 6, 7]; // Columns F, G, H

    for (j=0; j<points.length; j++) {
      let point = points[j]
      const pointYear=point['year'];
      const pointType=point['type'];
      const pointCategory=point['category']
      const pointNumber = point['number'];

      for (let i = 0; i < data.length; i++) {
        const row = data[i];
        const rowYear = row[yearIndex];
        const rowType = row[typeIndex];
        const rowCategory = row[categoryIndex];
        const rowNumber = row[numberIndex];
        const correctAnswer = row[answerColumnIndex];

        // Match the point
        if (
          parseInt(rowYear) == parseInt(pointYear) &&
          rowType == pointType &&
          rowCategory == pointCategory &&
          parseInt(rowNumber) == parseInt(pointNumber)
        ) {
          // Add images from hyperlinks
          let imageAdded = false;
          linkColumns.forEach(colIndex => {
            const richText = richTextData[i][colIndex];
            if (richText) {
              const link = richText.getLinkUrl();
              if (link) {
                try {
                  const fileId = link.match(/[-\w]{25,}/)[0];
                  const file = DriveApp.getFileById(fileId);
                  const blob = file.getBlob();
                  form.addImageItem().setTitle(
            `Year: ${rowYear}, Type: ${rowType}, Category: ${rowCategory}, Problem Number: ${rowNumber}`
          ).setImage(blob); // Add image above the question
                  imageAdded = true;
                } catch (e) {
                  Logger.log(`Error adding image for link ${link}: ${e.message}`);
                }
              }
            }
          });

          // Create a new question in the form
          const item = form.addMultipleChoiceItem();
          item.setTitle(
            "Risposta:"
          );

          // Set the choices for the question
          const choices = ['A', 'B', 'C', 'D', 'E'].map(choice => {
            if (choice === correctAnswer) {
              return item.createChoice(choice, true);
            }
            return item.createChoice(choice, false);
          });

          item.setChoices(choices);
          item.setPoints(5); // Points for correct answer
          item.setRequired(true); // Make the question mandatory
          break; // Move to the next point
        }
      }
    }
  });

  // Configure the quiz grading settings
  form.setLimitOneResponsePerUser(true);

  return form.getEditUrl();
}

function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

function getBase64Image(fileId) {
  try {
    const file = DriveApp.getFileById(fileId); // Fetch file by ID
    const blob = file.getBlob();              // Get file as blob
    const base64 = Utilities.base64Encode(blob.getBytes()); // Encode to Base64
    const mimeType = blob.getContentType();   // Get the MIME type of the file
    
    return { success: true, data: `data:${mimeType};base64,${base64}` };
  } catch (error) {
    return { success: false, message: `Failed to load file: ${error.message}` };
  }
}

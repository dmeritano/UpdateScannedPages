## UPDATE SCANNED PAGES

**Current versión**: 1.0

### Description

This application is designed to...

**Configuration File:** `appconfig.json`

**Sample:**

```json
{
  "dmsUri": "[URL API DMS]",
  "dmsUser": "[USER DMS]",
  "dmsPass": "[PASS DMS]",
  "dmsQuery": "[QUERY DMS]",
  "queryPageSize": 100,
  "secondsBetweenProcessedDocuments": 0.2,
  "sendEmailNotifications": true|false
}
```

**About some** `appconfig.json` **parameters:**

- `secondsBetweenProcessedDocuments` `0.00 to 2.00`
- `sendEmailNotifications` `true or false`

  - If set to ‘true’ the program will notify through an e-mail the result of each execution. To configure the mail follow these steps:

    1 - Set a system variable with name ‘FERNET_KEY’ and set as value a string of 32 characters long, where letters, numbers and special characters can be included.

    2 - From the command line, go to the folder where the program is (UpdateScannedPages.exe) and run it as follows:

    `UpdateSannedPages setup-mail`

    This will make the program make you enter all the necessary values to configure the mail.

### DISTRIBUTION

Use the script `build.bat` located in project root folder to generate executable (EXE) in the DIST folder of the project. Batch script also copies the configuration file to "DIST" folder and some BIN files needed for packages like Pdf2Image.

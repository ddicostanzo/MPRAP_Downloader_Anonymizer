# MPRAP_Downloader_Anonymizer

<h1>Medical Physics Residency Application Downloader and Anonymizer</h1>
Hello! Here is a small piece of software that can be used to download the Common Application for Medical Physics Residency applicants. It also contains a method to deidentify the data the best as possible.
<br/>
<h2>Prerequisites</h2>
<ol>
<li>Python 3.10+</li>
<li>I would suggest using PyCharm Community Edition to run this and create a virtual Python environment</li>
<li>Install packages from the requirements.txt into the virtual environment</li>
</ol>

<h2>Script Execution</h2>
It is possible to run this application as a script without an IDE. If you have the required packages installed in a virtual environment you can use the following syntax:
<ol>
<li>Download the applications using: python DownloadPDFs.py -d C:\...\MyDownloadLocation -u myusername -p mypassword -a mprapapplicationid</li>
<li>Rename the files that were downloaded with: python RenamePDFs.py -d C:\...\MyDownloadLocation --shuffle True/False</li>
<li>Run OCR with Adobe Acrobat on all of the applications</li>
<li>Anonymize the applications: python -a C:\...\ApplicationDirectory -o C:\...\OutputDirectory</li>
</ol>
Otherwise, you can manually fill in the variables and comment out the argparse logic and error handling in the if __name__ statements in each file.

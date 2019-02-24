# HTML Change Tracker
###### Track and be notified of changes on a web page
This script was built to notify me and my wife of when a particular item of clothing came into stock on zara.com because
they do not have a email notification system on their children's site.

## How it works
Using headless chrome, the html of the url specified in the config file is retrieved. Using the `BeautifulSoup` module,
a portion of the html is extracted for comparison. At the beginning of each run and any time there is a change, the html
is saved to the project folder as a timestamped html file.

When a change is detected, a notification is sent out via email while the script continues to run looking for
further changes.

## Config.yaml
The `config.yaml` file contains the settings for the script.

_Note: You must rename the file that comes with the project to `config.yaml`._

```yaml
project_name: Project Name Goes Here and is used to create a project folder
url: url to the page you want to follow
target:
  name: Your BeautifulSoup settings
  class: go here

sender:
  user: gmail account to send notification
  pwd: password
recipient:
  - email of recepient, one or more
  - send via text by using your cariers gateway like: 1234567890@txt.att.net

sleep:
  min: Minimum sleep time between checks
  max: max sleep time. Random choice between the 2 is chosen
```

## Journalist - Multimodal Browser Agents




VIDEOS GO HERE

- make an edit with screenshots of each step + total terminal output
- 



#### Overview

Foundationally, this works because the new OpenAI API 'define json for output/functions' stuff is really effective, and because gpt4o-mini is so cost-effective. This is my first time using the actual openAPI library and also Selenium, only had done traditional scraping in the past. 

This is a PoC agent that hooks up gpt-4o-mini to a browser. The multimodal large-language model can play the [Wikipedia Game](https://en.wikipedia.org/wiki/Wikipedia:Wiki_Game), winning frequently. 


#### Building/Utilization
---
functionally v2 is better but v1 is simple and has nice logging, easier to see how it works

**ocrlib is only macOS compatible right now.** 

TODO
- port OCR (tesseract) or do no ocr mode 
- better utilise config
- buy more api credits :(



````
#Python 3.10
#for dependencies see requirements.txt, sorry in advance. create a venv if you're into that sorta thing. 
#run once to generate default config.json in current directory, stick your openAI API key in it, etc.

#usage: python /path/to/journalv?.py <url> "Prompt"
#examples:
$ python v1/src/journalist.py http://pagewithinfo.com "Find what color the info should be?"

$ python v2/src/jv2.py http://pagewithinfo.com "Find what color the info should be?"

````

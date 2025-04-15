
## Install Guide

1. Install HTML to PDF tools

```
// Deprecated
brew install Caskroom/cask/wkhtmltopdf

// Run this
curl -L https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-2/wkhtmltox-0.12.6-2.macos-cocoa.pkg -O
sudo installer -pkg wkhtmltox-0.12.6-2.macos-cocoa.pkg -target ~
```

2. Install Requirements

```
pip install -r requirements.txt
```

3. Run 

```
python aliyun_crawler.py url
```
# HASS-plate-recognizer
Read number plates with https://platerecognizer.com/ which offers 2500 image recognitions per month for free. You will need to create an account and get your API token.

## Home Assistant setup
Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder). Then configure as below:

```yaml
image_processing:
  - platform: platerecognizer
    api_token: your_token
    source:
      - entity_id: camera.yours
```


## Development
Currently only the helper functions are tested, using pytest.
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip3 install -r requirements.txt`
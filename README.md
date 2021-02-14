# HASS-plate-recognizer
Read vehicle license plates with https://platerecognizer.com/ which offers free processing of 2500 images per month. You will need to create an account and get your API token.

This integration adds an image processing entity where the state of the entity is the number of license plates found in a processed image. Information about the vehicle which has the license plate is provided in the entity attributes, and includes the license plate number, [region/country](http://docs.platerecognizer.com/#countries), vehicle type, and confidence (in a scale 0 to 1) in this prediction. For each vehicle an `platerecognizer.vehicle_detected` event is fired, containing the same information just listed. Additionally, statistics about your account usage are given in the `Statistics` attribute, including the number of `calls_remaining` out of your 2500 monthly available.

**Note** this integration does NOT automatically process images, it is necessary to call the `image_processing.scan` service to trigger processing.

## Home Assistant setup
Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder). Then configure as below:

```yaml
image_processing:
  - platform: platerecognizer
    api_token: your_token
    save_file_folder: /config/images/platerecognizer/
    save_timestamped_file: True
    always_save_latest_jpg: True
    source:
      - entity_id: camera.yours
```

Configuration variables:
- **api_key**: Your api key.
- **save_file_folder**: (Optional) The folder to save processed images to. Note that folder path should be added to [whitelist_external_dirs](https://www.home-assistant.io/docs/configuration/basic/)
- **save_timestamped_file**: (Optional, default `False`, requires `save_file_folder` to be configured) Save the processed image with the time of detection in the filename.
- **always_save_latest_jpg**: (Optional, default `False`, requires `save_file_folder` to be configured) Always save the last processed image, no matter there were detections or not.
- **source**: Must be a camera.

## Development
Currently only the helper functions are tested, using pytest.
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip3 install -r requirements.txt`
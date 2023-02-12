# HASS-plate-recognizer
Read vehicle license plates with [Plate Recognizer ALPR](https://platerecognizer.com/) which offers free processing of 2500 images per month. You will need to create an account and get your API token.

This integration adds an image processing entity where the state of the entity is the number of license plates found in a processed image. Information about the vehicle which has the license plate is provided in the entity attributes, and includes the license plate number, [region/country](http://docs.platerecognizer.com/#countries), vehicle type, and confidence (in a scale 0 to 1) in this prediction. For each vehicle an `platerecognizer.vehicle_detected` event is fired, containing the same information just listed. Additionally, statistics about your account usage are given in the `Statistics` attribute, including the number of `calls_remaining` out of your 2500 monthly available.

If you have a paid plan that includes MMC (Make/Model/Colour) data you can received the orientation of the vehicle in the entity attributes.

You can also forward the LPR results straight to [ParkPow](https://parkpow.com), a parking management software and sister-company to Plate Recognizer.

If you have a local SDK licence, you can optionally specify the server address.

**Note** this integration does NOT automatically process images, it is necessary to call the `image_processing.scan` service to trigger processing.

## Home Assistant setup
Place the `custom_components` folder in your configuration directory (or add its contents to an existing `custom_components` folder). Then configure as below:

```yaml
image_processing:
  - platform: platerecognizer
    api_token: your_token
    regions:
      - gb
      - ie
    watched_plates:
      - kbw46ba
      - kfab726
    save_file_folder: /config/images/platerecognizer/
    save_timestamped_file: True
    always_save_latest_file: True
    mmc: True
    detection_rule: strict
    region: strict
    server: http://yoururl:8080/v1/plate-reader/

    source:
      - entity_id: camera.yours
```

Configuration variables:
- **api_key**: Your api key.
- **regions**: (Optional) A list of [regions/countries](http://docs.platerecognizer.com/?python#countries) to filter by. Note this may return fewer, but more specific predictions.
- **watched_plates**: (Optional) A list of number plates to watch for, which will identify a plate even if a couple of digits are incorrect in the prediction (fuzzy matching). If configured this adds an attribute to the entity with a boolean for each watched plate to indicate if it is detected.
- **save_file_folder**: (Optional) The folder to save processed images to. Note that folder path should be added to [whitelist_external_dirs](https://www.home-assistant.io/docs/configuration/basic/)
- **save_timestamped_file**: (Optional, default `False`, requires `save_file_folder` to be configured) Save the processed image with the time of detection in the filename.
- **always_save_latest_file**: (Optional, default `False`, requires `save_file_folder` to be configured) Always save the last processed image, no matter there were detections or not.
- **mmc**: (Optional, default `False`, requires a [paid plan](https://platerecognizer.com/pricing/) with the MMC (Make, Model, Colour) feature enabled.)  If enabled returns the orientation of the vehicle as a separate attribute containing Front/Rear/Unknown.
- **detection_rule**: (Optional) If set to `strict`, the license plates that are detected outside a vehicle will be discarded.
- **region**: (Optional) If set to `strict`, only accept the results that exactly match the templates of the specified region. For example, if the license plate of a region is 3 letters and 3 numbers, the value abc1234 will be discarded. For regions with vanity license plates (e.g. in us-ca), we do not recommend the use of Strict Mode. Otherwise, the engine will discard the vanity plates.
- **server**: (Optional, requires a [paid plan](https://platerecognizer.com/pricing/) Provide a local server address to use [On-Premise SDK](https://docs.platerecognizer.com/#on-premise-sdk)


- **source**: Must be a camera.

<p align="center">
<img src="https://github.com/robmarkcole/HASS-plate-recognizer/blob/main/docs/card.png" width="400">
</p>

<p align="center">
<img src="https://github.com/robmarkcole/HASS-plate-recognizer/blob/main/docs/main.png" width="800">
</p>

<p align="center">
<img src="https://github.com/robmarkcole/HASS-plate-recognizer/blob/main/docs/event.png" width="800">
</p>

## Making a sensor for individual plates
If you have configured `watched_plates` you can create a binary sensor for each watched plate, using a [template sensor](https://www.home-assistant.io/integrations/template/) as below, which is an example for plate `kbw46ba`:

```yaml
sensor:
  - platform: template
    sensors:
      plate_recognizer:
        friendly_name: "kbw46ba"
        value_template: "{{ state_attr('image_processing.platerecognizer_1', 'watched_plates').kbw46ba }}"
```

Depending on your license plate, you may recieve an template error due to variables not being able to start with a number. if so, here is another method to create the template sensor:
```yaml
sensor:
  - platform: template
    sensors:
      plate_recognizer:
        friendly_name: "kbw46ba"
        value_template: "{{ state_attr("image_processing.platerecognizer_1", "watched_plates")["kbw46ba"] }}"
```


## Video of usage
Checkout this excellent video of usage from [Everything Smart Home](https://www.youtube.com/channel/UCrVLgIniVg6jW38uVqDRIiQ)

[![](http://img.youtube.com/vi/t-XxCrdj_94/0.jpg)](http://www.youtube.com/watch?v=t-XxCrdj_94 "")

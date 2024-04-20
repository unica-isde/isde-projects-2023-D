# Pull Request Description

In this Pull Request we implement and solve:

Issue #1 - Image Histogram,
Issue #2 - Image Transformation,
Issue #3 - Download Results Button,
Issue #4 - Upload Image Button.

You can find a description on how the Issues were solved here:

## Issue #1 - Image Histogram

To solve this issue we created a new route "/histograms". In the GET request it renders the template "histogram_select.html", where the user chooses the image for which the histogram will be computed from a list of images.
A dedicated form has been created "histogram_form.py".
In the POST request the result will be rendered using the JavaScript library called Chart.js after having received the histogram data from the backend.
To calculate the data we implemented in the backend the function named "calculate_histogram" that uses the numpy function "np.histogram".

## Issue #2 - Image Transformation

To solve this issue we created a new route "/classify_transform". In the GET request it renders the "transformation_select.html" where the user chooses the model he wants to use to classify the image and the image itself from a list of images.
A dedicated form has been created "transformation_form.py".
Below that there is a button that if pressed opens a Modal where the user can modify the Color, the Brightness, the Contrast and the Sharpness of the image. All those values also have default values for when the user leaves them blank.
When the user presses the Submit button the POST will render the "transformation_output.html" and the classification will be done for the Enhanced image. The Enhanced Image and the original one are shown side by side.

The Enhanced image is computed in the backend using PIL.
The "transform_image" function opens the image and applies the enhancements requested by the user. Then the enhanced image is passed to the "convert_image" function that will convert it to a base64 string and sent to the frontend to be displayed. The image is not anymore saved in the server memory to solve concurrency and file storage problems.

## Issue #3 - Download Results Button

In this issue two APIs are implemented, the first one is outputJSON (GET) which takes into input the classification scores object and then returns a JSONResponse object containing the classification values.
The second API is outputPNG (GET) which is useful to have the png version of the plot downloaded locally, this is done by taking classification scores as a parameter to put in into a figure that plots the data using matplotlib and then Byte streams it to the frontend.

## Issue #4 - Upload Image Button

To solve this issue we created a new route "/uploadImage". The GET request it renders the "upload_select.html" where the user chooses the model he wants to use to classify the image and where he can browse to his local files and upload an image that he wants to clissify.
After the "Submit" button is pressed, a new route "/classifyUpload" with POST method checks if the file selected is an image through the check_errors(image) function.
If the selected file is not an image, an exception is raised, the "upload_select.html" file is rendered again and the user gets notified that he selected a wrong file.
If the selected file is indeed an image, the UploadFile image is transformed into a bytes array so that it can be returned to the frontend and the image can be shown without saving it.
Then the "classify_image" function is called to classify the uploaded image.
At last the "upload_output.html" is rendered, the image and the plot are shown to the user. 
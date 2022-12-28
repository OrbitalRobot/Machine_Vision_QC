# **Machine_Vision_QC**
*This was a final project completed in a short timeframe for a university machine vision course.  It is unpolished and was uploaded to demonstrate what was learned during the course.*

Videos of the final student solution can be seen here: [Physical Build](https://youtu.be/jEyg4VlbFEg), [Operation](https://youtu.be/skzYGORNM7I)




## **Challenge Description**
Using an OpenMV H7 camera, the OpenMV IDE, and the physical materials of your choice, build a machine vision system for performing quality control of manufactured circuit boards.




### **Time Allotted**
The student had approximately 40 working hours to do the following:
- Design and build a physical machine vision system
- Write and test the code against a batch of 90 circuit boards
- Document and upload the results




### **Test Parts**
The circuit boards to be tested were 3D printed examples that came in 4 colors printed at varying densities, with slight dimensional variability.
A complete circuit board had 44 components, any one of which could be missing on a given board.
Criteria for an acceptable board was that all components were present in their designated locations.
The machine's role was merely to detect if any component was missing.  If any one component was missing, the board was to be rejected.  It was not required to determine the number of missing components, their location, or the color of the board.

![image](https://user-images.githubusercontent.com/121198760/209278631-62b89ca1-4f48-412c-85bc-b2513a12f719.png)![image](https://user-images.githubusercontent.com/121198760/209279285-9dc8def7-2e07-499a-b86f-aee460a7e02a.png)![image](https://user-images.githubusercontent.com/121198760/209279349-760ef157-1a11-4f38-9c7d-4000502a5d05.png)




### **Performance Requirements**
As a benchmark for comparison, the students were shown a video of a human inspecting the circuit boards by hand.  The human processed roughly 3 boards per minute, and detected rejectable boards with approximately 85% accuracy.

The student's machine vision solution was expected to be at least as fast as the human and more accurate, so as to provide a reasonable business case for implementing such a system.




## **Student Solution**
---

![image](https://user-images.githubusercontent.com/121198760/209278962-3642c830-c9c4-41c3-af2b-f0c3ffe7fcfe.png)
![image](https://user-images.githubusercontent.com/121198760/209279118-afe49a41-1024-464d-8cc9-782cc6bac036.png)
![image](https://user-images.githubusercontent.com/121198760/209285876-0e8e0cf9-21e6-48c1-9628-8feef83889c1.png)



### **Physical System Build**
The student chose to build a backlit, partially enclosed structure with the camera mounted at the top, and parts placed on a fixture on the backlight at the bottom.
- Extruded aluminum components, a backlight, and dense foam board were purchased.
- A fixture was designed and printed to hold the OpenMV H7 camera on the aluminum frame.
- The backlight was covered with a black cardboard piece with a cutout large enough for a tool holding a ciruit board to fit
- A frame was 3D printed to hold circuit boards and adhered to the cardboard piece on the backlight

The rationale behind this approach was as follows:
- Minimize the effects of exterior lighting
- Maximize contrast between a thicker area where a component is, and a thinner area where a component is missing
- Mitigate the possibility for the light source to create shadows or glare on the test board
- Locate the parts as repeatably as possible to maximize the probability of detecting the smallest possible components, which were 8mm x 3mm x 2mm (L x W x D)
- Leave the front of the machine open for easy part placement and removal
- Build the frame in such a way that the camera can be translated in the X, Y, and Z axes to control the size and location of the image frame during initial testing




### **Problem Solving Approach to Coding A Solution**
The student's approach began with determining which variables appeared to be the most problematic, and base a code solution on mitigating the effects of those variables.
Specifically, the variables of focus were:
- **Translucency**
    Boards of different colors and densities would let different amounts of light through, making it difficult to tell if a component was missing based solely on light       intensity.  A robust solution would begin with evaluating the boards in a manner that compensated for translucency deltas or removed their effects entirely.
- **Part Location**
    Fortunately, the spacing between the smallest components was larger than the overall length and width variability in the whole circuit boards themselves.
    This indicated to the student that if the boards were positioned with a tolerance equal to their dimensional variability, the smallest components could be detected       by using unique regions of interest for each component.  This was achieved by the physical frame used to locate the part reliably that was mentioned above, in         the design rationale for the physical system build .
    



### **Solution Overview**
  **First, Compensate For Translucense**

With the parts positioned reliably enough, an area of the board that is always blank was examined with test shots on several boards.  On each image, a histogram with 256 bins was created, and the bin with the highest values was noted.  Then multiple shots were taken with different exposure times and the histogram bin with the maximum value was noted for each exposure time.  From this it was determined that by adjusting the exposure time for a given board, one could get the histogram bin with the maximum value to be between 200 and 220 reliably.  This would be used as a method for calibrating exposure time to normalize for varying levels of translucense moving forward.  This blank area on the board shall be referred to as the calibration area from this point on.

In general, different colored boards had different ranges of acceptable exposure times.  To narrow the range of possible exposure times, the color of the board was determined.  A QVGA color image was taken and the L-A-B values from the histogram of the board's calibration area were converted to RGB values.  After testing a sample set of boards of each color, an average RGB set of values for a given colored board was recorded.  To determine the color of a given board, its calibration area's RGB values were compared against dicitonaries of known RGB values within a certain range to check for a match.

Once the color of the board was known, a small set of possible exposure times was checked for an acceptabe time.  It was determined that iterating through the range of acceptable times from the minimum to the maximum time in 1000 microsecond increments provided the most reliable results, and in an acceptable amount of time.  Given the limited working time the student had for the project, the exposure time search algorith was not optimized any further, though a binary search approach would've been the student's next step.




  **Then Check For Each Component's Presence**

A static dictionary of ROIs was built ahead of time with one entry for each of the 44 components that should be checked on a board.  Then, a grayscale image of the test board is taken.  The grayscale image is reduced to a binary black & white image based on a given threshold determined ahead of time during testing.  Then the black pixels in each component's ROI are counted.  They are compared to a dictionary of known black pixel counts from acceptable boards.  If any ROI's black pixel count differs by more than a certain margin from the good board's, the component in that ROI is deemed missing and the board fails.  In practice, this process had to be done with 2 different binary image thresholds.  One threshold worked best for evaluating components near the perimeter of the board, and one threshold worked better for evaluating components on the rest of the board.  So 2 grayscale shots are taken and converted to binary images, each with one of two binary thresholds.




## **Results**
The chosen solution allowed a human operator to process 5-6 boards per minute through the machine, and rejected boards with a 97% accuracy rate.  It was determined that the boards that were called inaccurately were missed as a result of changing external lighting conditions.  To further mitigate this on improved versions of the system, a door on the front of the machine that opens and closes automatically would be installed to block out all external light when examining a board.

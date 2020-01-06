---
title: 'Aura: Inside-out Electromagnetic Controller Tracking'
authors: [whitmire, parizi, patel]
conference: 17th ACM International Conference on Mobile Systems, Applications, and Services (MobiSys), 2019
date: 2019-06-17
pdf: /pdfs/aura.pdf
video: https://www.youtube.com/watch?v=P6TU2hA_R5w&feature=youtu.be
video_embed: '<iframe width="560" height="315" src="https://www.youtube.com/watch?v=P6TU2hA_R5w&feature=youtu.be" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
image: /images/pubs/aura.png
thumbnail: /images/pubs/aura_thumb.jpg
caption: Aura uses custom non-orthogonal coils on the headset and a 3-axis receiver coil within the handheld controller to reconstruct the 6-DoF pose of the controller.
citation: |
  Eric Whitmire, Farshid Salemi Parizi, and Shwetak Patel. 2019. Aura: Inside-out Electromagnetic Controller Tracking. In Proceedings of the 17th Annual International Conference on Mobile Systems, Applications, and Services (MobiSys ’19). Association for Computing Machinery, New York, NY, USA, 300–312. DOI:https://doi-org.edu/10.1145/3307334.3326090
abstract: |
  The ability to track handheld controllers in 3D space is critical for interaction with head-mounted displays, such as those used in virtual and augmented reality systems. Today’s systems commonly rely on dedicated infrastructure to track the controller or only provide inertial-based rotational tracking, which severely limits the user experience. Optical inside-out systems offer mobility but require line-of-sight and bulky tracking rings, which limit the ubiquity of these devices. In this work, we present Aura, an inside-out electromagnetic 6-DoF tracking system for handheld controllers. The tracking system consists of three coils embedded in a head-mounted display and a set of orthogonal receiver coils embedded in a handheld controller. We propose a novel closed-form and computationally simple tracking approach to reconstruct position and orientation in real time. Our handheld controller is small enough to fit in a pocket and consumes less than 15 mA of current, allowing it to operate for multiple days on a typical battery. Aura achieves a median tracking error of 5.5 mm and 0.8 degrees in 3D space within arm's reach.
bibtex: |
    @inproceedings{Whitmire:2019:AIE:3307334.3326090,
     author = {Whitmire, Eric and Salemi Parizi, Farshid and Patel, Shwetak},
     title = {Aura: Inside-out Electromagnetic Controller Tracking},
     booktitle = {Proceedings of the 17th Annual International Conference on Mobile Systems, Applications, and Services},
     series = {MobiSys '19},
     year = {2019},
     isbn = {978-1-4503-6661-8},
     location = {Seoul, Republic of Korea},
     pages = {300--312},
     numpages = {13},
     url = {http://doi.acm.org/10.1145/3307334.3326090},
     doi = {10.1145/3307334.3326090},
     acmid = {3326090},
     publisher = {ACM},
     address = {New York, NY, USA},
     keywords = {controller, electromagnetic tracking, head-mounted display, mixed reality, virtual reality},
    }
---

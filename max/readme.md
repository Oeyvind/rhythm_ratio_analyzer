The max implementation of the rhythm analyzer and generator is distributed in this directory as 'frozen' Max for Live device, self contained and without needing any further dependencies or libraries. This device can also be run directly in Max without using Ableton Live.

In addition, there is a 'source' directory containing max patches, abstractions and max for live devices in current development.

As the implementation relies extensively on the array objects introduced in Max 9, these devices requires Max version 9+ or Ableton Live 12+ to work.


Both the analysis and generator stages are implemented with native vanilla Max objects and work without the python back end or other external objects. The patches still in development might use externals like the Bach library for score visualization.



Daniel Formo, NTNU, 2025
daniel.formo@ntnu.no

# Radio Dabby

An online radio station playing chaotic variations of classical music based on ["Musical variations from a chaotic mapping"](https://dspace.mit.edu/bitstream/handle/1721.1/27282/Dabby_Diana_PhD_1995.pdf?sequence=1) by Dr. Diana Dabby

## Dependencies
* Chaotic Mapping 
  * `python3` - 3.7 recommended; following packages used to generate chaotic variations:
    * `scipy`
    * `numpy`
    * `music21`

* Source Files and Synthesis
  * [Kunst Der Fuge](http://kunstderfuge.com) - Collection of community contributed MIDI files
  * [Pianoteq 7](https://modartt.com/pianoteq) - Physically modelled piano synthesizer
  
* Internet streaming radio broadcast
  * `icecast2` - highly reliable streaming server for audio 
  * `ffmpeg` - compiled from source with `libfdk_aac` support


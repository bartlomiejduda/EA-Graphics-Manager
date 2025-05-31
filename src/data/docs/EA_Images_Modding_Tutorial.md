# EA Images Modding Tutorial

Tutorial last update date: 31.05.2025<br>
Tutorial version: 1.0

## Info

This tutorial aims to teach you how to mod graphics in EA games
with file extensions like **SSH, XSH, FSH** etc.
You'll learn how to export images, edit them and import them back to **EA Shape** files.


## Prerequisites

You need to have downloaded latest version of **EA Graphics Manager**.
To check if you are up to date, please go to
**[program's release page](https://github.com/bartlomiejduda/EA-Graphics-Manager/releases)**
and search for "latest" version.


## Compatibility

Remember that currently not all image types are supported for modding.
EA file format supports over 100 image types and each image type
can be decoded and encoded in a different way.
To see if your game or image type is supported, please go to
**[readme's page](https://github.com/bartlomiejduda/EA-Graphics-Manager/blob/main/README.md)**
and scroll down to **"Image formats support table"** which can tell you what is supported.

Please also note that some features like:
- replacing images with mipmaps
- replacing compressed images
- aligning image data
- compressing whole Shape files

may NOT be supported at the moment, but this can change in the future program's versions.

## Getting EA Image Files

To mod games, first you need to get image files.
Sometimes files are directly stored in game's directory, like in PC games.
But more often files are packed inside custom archives. In case of older EA games
all files are stored inside archives with **BIG** or **VIV** file extension.
There are some programs capable of opening and editing them like **BigGUI**,
**Final BIG Editor**, **big4f**. There are also a lot of quickBMS scripts written
by the community to deal with the archives.

Once you'll download a proper program or script, you can use it to extract data
from the archive and copy it to some temporary mod directory.
Here's an example how it should look after extracting:

<img src="..\img\modding_tutorial\files_to_mod.png">

## Extracting/Editing Images

When you have some EA graphics with extensions like
SSH, MSH, XSH etc. extracted, you can run **EA Graphics Manager**
by double-clicking EXE file.
Then try to open one of the images by going to **File > Open File** or
by pressing **CTRL+O** on your keyboard.

<img src="..\img\modding_tutorial\file_open.png">

Then select your image file. For this tutorial I use "001-merlin_flat.ssh"
from "Harry Potter and the Chamber of Secrets" on PS2 console.

Once opened in the program, you can click on one of the images listed
on the left panel to preview image. In this example there is only one image entry
named "001".

<img src="..\img\modding_tutorial\image_preview.png">

From the "Entry Header" section you can learn that's image you opened
is a "type 2" image which is PAL8. That's indexed image, it uses
additional palette to map colors.

Now right click on "001" entry and select "**Export Image as DDS/PNG/BMP**"
option.

<img src="..\img\modding_tutorial\image_export_import.png">

Now choose one of the available extensions e.g. DDS and save file on disk.

After saving, you can edit image in an external editor like GIMP.
For this example, I've decided to paint letters "RGB" on the image:

<img src="..\img\modding_tutorial\image_gimp.png">

If you're working with indexed images like PAL4 or PAL8,
you can deal with the image quantization before saving your changes.
To do this, you can go to **Image > Mode > Indexed** option
and set 256 colors for PAL8 and 16 colors for PAL4.

<img src="..\img\modding_tutorial\image_indexed.png">

This step is optional and if you forget to do this,
EA Graphics Manager will handle image quantization automatically.
And if you're working with linear data (like RGBA8888),
there is no need to do this at all.

Now save your changes in GIMP and return to EA Graphics Manager.

## Importing Images

If you have image file saved after making some changes in image-editing
software like GIMP, you can now proceed with import.

To do this, you have to right-click on the image entry in the left panel,
in this case it will be "001". Please select "**Import image from "DDS/PNG/BMP**"
and select edited file from disk.

<img src="..\img\modding_tutorial\image_export_import.png">

After successful import, you should see green checkmark symbol on
the left panel:

<img src="..\img\modding_tutorial\image_checkmark.png">

Now you can save your file. Please click on the EA Shape entry
and select "**Save File As...**" option:

<img src="..\img\modding_tutorial\file_save_as.png">

And that's it. You have successfully edited EA Shape file.
Now you can replace output file in game files and then test your changes
in game.

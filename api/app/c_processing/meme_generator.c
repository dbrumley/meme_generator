#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wand/MagickWand.h>

void ThrowWandException(MagickWand *wand)
{
    char *description;
    ExceptionType severity;
    description = MagickGetException(wand, &severity);
    (void)fprintf(stderr, "%s %s %lu %s\n", GetMagickModule(), description);
    description = (char *)MagickRelinquishMemory(description);
    exit(EXIT_FAILURE);
}

void DrawTextOnImage(MagickWand *image_wand, const char *text, const int y_offset)
{
    DrawingWand *draw_wand = NewDrawingWand();
    PixelWand *color = NewPixelWand();
    PixelSetColor(color, "white");
    DrawSetFillColor(draw_wand, color);
    DrawSetFontSize(draw_wand, 40);
    DrawSetGravity(draw_wand, CenterGravity);

    if (MagickAnnotateImage(image_wand, draw_wand, 0, y_offset, 0, text) == MagickFalse)
    {
        ThrowWandException(image_wand);
    }

    DestroyDrawingWand(draw_wand);
    DestroyPixelWand(color);
}

void stack_recursion()
{
    char buff[0x1000];
    while (1)
    {
        stack_recursion();
    }
}

void insecure_code(MagickWand *image_wand, const char *top_text, const char *bottom_text)
{
    printf("Starting insecure code...");

    char top_text_buffer[64];
    char bottom_text_buffer[64];

    // Stack overflows
    strcpy(top_text_buffer, top_text);
    strcpy(bottom_text_buffer, bottom_text);
    printf("Top: %s bottom: %s\n", top_text_buffer, bottom_text_buffer);

    size_t width = MagickGetImageWidth(image_wand);
    size_t height = MagickGetImageHeight(image_wand);

    // integer overflow 0x7FFFFFFF+1=0
    // 0x7FFFFFFF+2 = 1
    // will cause very large/small memory allocation.
    int size1 = width + height;

    // Integer underflow 0-1 = -1
    int size2 = width - height + 100;

    // divide by zero
    int size3 = width / height;

    printf("width: %d height: %d size1: %d size2: %d size3: %d\n",
           width, height, size1, size2, size3);

    size_t blob_length;
    char *buff1 = (char *)malloc(size1);
    unsigned char *blob = MagickGetImagesBlob(image_wand, &blob_length);
    // heap buffer overflow.
    memcpy(buff1, blob, blob_length);
    printf("Using buff1: %p\n", buff1);

    // double free
    if (size1 / 2 == 0)
    {
        free(buff1);
    }
    else
    {
        // use after free
        if (size1 / 3 == 0)
        {
            buff1[0] = 'a';
        }
    }

    int size4 = width * height;
    if (size4 / 2 == 0)
    {
        // stack exhaustion here
        stack_recursion();
    }

    // buff1 memory leak.

    printf("Done with tricky security code....\n");
}

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        fprintf(stderr, "Usage: %s <input_image> <top_text> <bottom_text> <output_image>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_image_path = argv[1];
    const char *top_text = argv[2];
    const char *bottom_text = argv[3];
    const char *output_image_path = argv[4];

    MagickWandGenesis();
    MagickWand *image_wand = NewMagickWand();

    if (MagickReadImage(image_wand, input_image_path) == MagickFalse)
    {
        ThrowWandException(image_wand);
    }

    insecure_code(image_wand, top_text, bottom_text);

    size_t num_frames = MagickGetNumberImages(image_wand);
    for (size_t i = 0; i < num_frames; i++)
    {
        MagickSetIteratorIndex(image_wand, i);
        DrawTextOnImage(image_wand, top_text, -300);   // Adjust the y_offset as needed
        DrawTextOnImage(image_wand, bottom_text, 300); // Adjust the y_offset as needed
    }

    if (MagickWriteImages(image_wand, output_image_path, MagickTrue) == MagickFalse)
    {
        ThrowWandException(image_wand);
    }

    DestroyMagickWand(image_wand);
    MagickWandTerminus();

    return EXIT_SUCCESS;
}

# Define the compiler
CC = gcc

# Define compiler flags
CFLAGS = -Wall -Wextra -O2 `pkg-config --cflags MagickWand`

# Define linker flags
LDFLAGS = `pkg-config --libs MagickWand`

# Define the target executable
TARGET = meme_generator

# Define the source files
SRCS = meme_generator.c

# Define the object files
OBJS = $(SRCS:.c=.o)

# Default target
all: $(TARGET)

# Rule to build the target executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

# Rule to build object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean up build files
clean:
	rm -f $(TARGET) $(OBJS)

# Phony targets
.PHONY: all clean

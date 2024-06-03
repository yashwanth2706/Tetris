#Compiler(Name)-> g++
#AllProgramFiles(.cpp)-> main.cpp game.cpp grid.cpp position.cpp colors.cpp block.cpp blocks.cpp
#Output Argument For (Compiler)-> -o
#Output To FileName(Binary)-> TetrisGame
#-L/path/to/raylib (Optional/ Add If Necessary) ->  -L/home/yashwanth/raylib
#Flags for (Linking)-> -lraylib -lGL -lm -lpthread -ldl -lrt -lX11

#In the below command PATH/TO/RAYLIB has been added for compilation process  (OPTIONAL)
#Adding raylib path helps when raylib is not made available systemwide

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
#g++ main.cpp game.cpp grid.cpp position.cpp colors.cpp block.cpp blocks.cpp -o TetrisGame -L/home/yashwanth/raylib -lraylib -lGL -lm -lpthread -ldl -lrt -lX11
#--------------------------------------------------------------------------------------------------------------------------------------------------------------


#When raylib is made available systemwide below command works
g++ main.cpp game.cpp grid.cpp position.cpp colors.cpp block.cpp blocks.cpp -o TetrisGame -lraylib -lGL -lm -lpthread -ldl -lrt -lX11
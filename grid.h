#pragma once //avoids duplicate definitions
#include<vector>
#include<raylib.h>

class Grid {

    public:
        Grid();
        void Initialize();
        void Draw();
        bool IsCellOutSide(int row, int column);
        bool IsCellEmpty(int row, int column);
        void Print();
        int ClearFullRows();
        int grid[20][10];

    private:
        bool IsRowFull(int row);
        void ClearRow(int row);
        void MoveRowDown(int row, int numRows);
        int numRows;
        int numCols;
        int cellSize;
        std::vector<Color> colors;
};

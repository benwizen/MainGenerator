#pragma once
#include "Point.h"

class Line
{
public:
	Line( const Point& p1, const Point& p2 );
	~Line();

public:
	bool onLine( const Point& p2 );

private:
	void updateSlope();
	void updateOffset();

private:
	Point p1;
	Point p2;
	double slope;
	double offset;
};


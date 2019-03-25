#pragma once

#include <iostream>
#include <string>

using namespace std;

class Point
{
public:
	//Ctors Dtors
	//Point();
	Point(int x = 0, int y = 0);
	Point(int x) : m_x(x), m_y(2*x) {}
	Point(Point& pnt) : m_x(pnt.m_x), m_y(pnt.m_y) {}
	Point operator+(const Point& p) const;
	~Point();

public:
	//set get
	void setX(int x);
	void setY(int y);
	void setXY(int x, int y);
	int getX()const { return m_x; }
	int getY()const { return m_y; }

public:
	//methods
	void print();
	void movePoint(int x, int y);

private:
	int m_x;
	int m_y;
};


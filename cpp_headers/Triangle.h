#pragma once
#include "Point.h"


class Triangle
{
public:
	Triangle();
	Triangle( const Point& p1, const Point& p2, const Point& p3 );
	~Triangle();

public:
	void print();
	void setPoints( const Point& p1, const Point& p2, const Point& p3 );
	void setP1( const Point& p1 );
	Point getP1() { return m_p1; }

private:
	bool m_valid;
	Point m_p1;
	Point m_p2;
	Point m_p3;
	//Line m_p4;
};


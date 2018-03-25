#ifndef TQEC_OPTIMIZER_VECTOR3D_HPP
#define TQEC_OPTIMIZER_VECTOR3D_HPP

#include <iostream>
#include <cmath>

class Vector3D {
public:
    double x;
    double y;
    double z;

    Vector3D()
            : x(0.0),
              y(0.0),
              z(0.0)
    { }

    Vector3D(const double xx,
             const double yy,
             const double zz)
            : x(xx),
              y(yy),
              z(zz)
    { }

    Vector3D& assign(const double xx,
                     const double yy,
                     const double zz) {
        x = xx;
        y = yy;
        z = zz;
        return *this;
    }

    double w() const { return this->x; }
    double h() const { return this->y; }
    double d() const { return this->z; }

    double dist(const Vector3D& p) const {
        return std::abs(this->x - p.x) + std::abs(this->y - p.y) + std::abs(this->z - p.z);
    }
};

inline
std::ostream & operator<<(std::ostream & os, const Vector3D& v) {
    os << '(' << v.x << ", " << v.y << ", " << v.z << ')';
    return os;
}

#endif //TQEC_OPTIMIZER_VECTOR3D_HPP

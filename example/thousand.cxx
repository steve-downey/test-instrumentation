#include <iostream>
#include "pow.h"
int main() {
  constexpr int x = pow(2, 1000, 100);
  std::cout << x << std::endl;
}

#include "instrument_bridge.hpp"

#include <sstream>

namespace probepilot {

InstrumentBridge::InstrumentBridge(ScpiSessionConfig cfg) : cfg_(std::move(cfg)) {}

std::string InstrumentBridge::idn() {
  // Stub: wire to libusb/VISA in the bench build.
  return "PROBEPILOT,STUB,0,0";
}

std::vector<double> InstrumentBridge::parse_scope_csv(const std::string& csv_blob) {
  std::vector<double> samples;
  std::istringstream in(csv_blob);
  std::string line;
  while (std::getline(in, line)) {
    if (line.empty() || line[0] == '#') continue;
    try {
      samples.push_back(std::stod(line));
    } catch (...) {
      // skip non-numeric rows (headers)
    }
  }
  return samples;
}

}  // namespace probepilot

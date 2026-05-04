#pragma once

#include <string>
#include <vector>

namespace probepilot {

struct ScpiSessionConfig {
  std::string resource; // e.g. TCPIP0::192.168.1.10::INSTR
  int timeout_ms{5000};
};

/// High-level SCPI bridge; implementation dispatches to USB/TCP-VISA in production.
class InstrumentBridge {
 public:
  explicit InstrumentBridge(ScpiSessionConfig cfg);
  std::string idn();
  std::vector<double> parse_scope_csv(const std::string& csv_blob);

 private:
  ScpiSessionConfig cfg_;
};

}  // namespace probepilot

use std::fmt;

/// SI prefix multipliers
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SiPrefix {
    Femto,  // f  1e-15
    Pico,   // p  1e-12
    Nano,   // n  1e-9
    Micro,  // u  1e-6
    Milli,  // m  1e-3
    None,   //    1e0
    Kilo,   // k  1e3
    Mega,   // M  1e6 — SPICE uses "meg"
    Giga,   // G  1e9
    Tera,   // T  1e12
}

impl SiPrefix {
    pub fn multiplier(self) -> f64 {
        match self {
            Self::Femto => 1e-15,
            Self::Pico => 1e-12,
            Self::Nano => 1e-9,
            Self::Micro => 1e-6,
            Self::Milli => 1e-3,
            Self::None => 1.0,
            Self::Kilo => 1e3,
            Self::Mega => 1e6,
            Self::Giga => 1e9,
            Self::Tera => 1e12,
        }
    }

    /// SPICE-format suffix string
    pub fn spice_suffix(self) -> &'static str {
        match self {
            Self::Femto => "f",
            Self::Pico => "p",
            Self::Nano => "n",
            Self::Micro => "u",
            Self::Milli => "m",
            Self::None => "",
            Self::Kilo => "k",
            Self::Mega => "meg",
            Self::Giga => "g",
            Self::Tera => "t",
        }
    }

    /// Best prefix for a given value to keep mantissa in [1, 1000)
    pub fn best_for(value: f64) -> Self {
        let abs = value.abs();
        if abs == 0.0 {
            return Self::None;
        }
        let prefixes = [
            Self::Femto,
            Self::Pico,
            Self::Nano,
            Self::Micro,
            Self::Milli,
            Self::None,
            Self::Kilo,
            Self::Mega,
            Self::Giga,
            Self::Tera,
        ];
        for &p in prefixes.iter().rev() {
            if abs >= p.multiplier() {
                return p;
            }
        }
        Self::Femto
    }
}

/// Electrical unit types
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum UnitKind {
    Volt,
    Ampere,
    Ohm,
    Farad,
    Henry,
    Hertz,
    Second,
    Watt,
    Degree,
    Unitless,
}

impl UnitKind {
    pub fn symbol(self) -> &'static str {
        match self {
            Self::Volt => "V",
            Self::Ampere => "A",
            Self::Ohm => "Ohm",
            Self::Farad => "F",
            Self::Henry => "H",
            Self::Hertz => "Hz",
            Self::Second => "s",
            Self::Watt => "W",
            Self::Degree => "°C",
            Self::Unitless => "",
        }
    }
}

/// A unit descriptor: prefix + kind. Used as the RHS of `value @ unit`.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Unit {
    pub prefix: SiPrefix,
    pub kind: UnitKind,
}

impl Unit {
    pub const fn new(prefix: SiPrefix, kind: UnitKind) -> Self {
        Self { prefix, kind }
    }
}

/// A value with unit annotation
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct UnitValue {
    /// Value in base SI units (e.g. 1kOhm → 1000.0)
    pub value: f64,
    pub unit: Unit,
}

impl UnitValue {
    pub fn new(value: f64, unit: Unit) -> Self {
        Self {
            value: value * unit.prefix.multiplier(),
            unit: Unit::new(SiPrefix::None, unit.kind),
        }
    }

    /// Raw construction (value already in base units)
    pub fn raw(value: f64, kind: UnitKind) -> Self {
        Self {
            value,
            unit: Unit::new(SiPrefix::None, kind),
        }
    }

    /// SPICE-format string: "1k", "10p", "100n", "3.3"
    pub fn str_spice(&self) -> String {
        let prefix = SiPrefix::best_for(self.value);
        let mantissa = self.value / prefix.multiplier();
        let suffix = prefix.spice_suffix();
        // Round to avoid floating point artifacts
        let rounded = mantissa.round();
        if (mantissa - rounded).abs() < 1e-9 && rounded.abs() < 1e15 {
            format!("{}{}", rounded as i64, suffix)
        } else {
            format!("{}{}", mantissa, suffix)
        }
    }

    pub fn as_f64(&self) -> f64 {
        self.value
    }
}

impl fmt::Display for UnitValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let prefix = SiPrefix::best_for(self.value);
        let mantissa = self.value / prefix.multiplier();
        write!(
            f,
            "{}{}{}",
            mantissa,
            prefix.spice_suffix(),
            self.unit.kind.symbol()
        )
    }
}

impl From<UnitValue> for f64 {
    fn from(uv: UnitValue) -> f64 {
        uv.value
    }
}

// ── Pre-defined unit constants (used as RHS of `@` in Python) ──

// Volts
pub const U_V: Unit = Unit::new(SiPrefix::None, UnitKind::Volt);
pub const U_MV: Unit = Unit::new(SiPrefix::Milli, UnitKind::Volt);
pub const U_UV: Unit = Unit::new(SiPrefix::Micro, UnitKind::Volt);

// Amperes
pub const U_A: Unit = Unit::new(SiPrefix::None, UnitKind::Ampere);
pub const U_MA: Unit = Unit::new(SiPrefix::Milli, UnitKind::Ampere);
pub const U_UA: Unit = Unit::new(SiPrefix::Micro, UnitKind::Ampere);
pub const U_NA: Unit = Unit::new(SiPrefix::Nano, UnitKind::Ampere);

// Ohms
pub const U_OHM: Unit = Unit::new(SiPrefix::None, UnitKind::Ohm);
pub const U_KOHM: Unit = Unit::new(SiPrefix::Kilo, UnitKind::Ohm);
pub const U_MOHM: Unit = Unit::new(SiPrefix::Mega, UnitKind::Ohm);

// Farads
pub const U_F: Unit = Unit::new(SiPrefix::None, UnitKind::Farad);
pub const U_MF: Unit = Unit::new(SiPrefix::Milli, UnitKind::Farad);
pub const U_UF: Unit = Unit::new(SiPrefix::Micro, UnitKind::Farad);
pub const U_NF: Unit = Unit::new(SiPrefix::Nano, UnitKind::Farad);
pub const U_PF: Unit = Unit::new(SiPrefix::Pico, UnitKind::Farad);
pub const U_FF: Unit = Unit::new(SiPrefix::Femto, UnitKind::Farad);

// Henrys
pub const U_H: Unit = Unit::new(SiPrefix::None, UnitKind::Henry);
pub const U_MH: Unit = Unit::new(SiPrefix::Milli, UnitKind::Henry);
pub const U_UH: Unit = Unit::new(SiPrefix::Micro, UnitKind::Henry);
pub const U_NH: Unit = Unit::new(SiPrefix::Nano, UnitKind::Henry);

// Hertz
pub const U_HZ: Unit = Unit::new(SiPrefix::None, UnitKind::Hertz);
pub const U_KHZ: Unit = Unit::new(SiPrefix::Kilo, UnitKind::Hertz);
pub const U_MHZ: Unit = Unit::new(SiPrefix::Mega, UnitKind::Hertz);
pub const U_GHZ: Unit = Unit::new(SiPrefix::Giga, UnitKind::Hertz);

// Seconds
pub const U_S: Unit = Unit::new(SiPrefix::None, UnitKind::Second);
pub const U_MS: Unit = Unit::new(SiPrefix::Milli, UnitKind::Second);
pub const U_US: Unit = Unit::new(SiPrefix::Micro, UnitKind::Second);
pub const U_NS: Unit = Unit::new(SiPrefix::Nano, UnitKind::Second);
pub const U_PS: Unit = Unit::new(SiPrefix::Pico, UnitKind::Second);

// Watts
pub const U_W: Unit = Unit::new(SiPrefix::None, UnitKind::Watt);
pub const U_MW: Unit = Unit::new(SiPrefix::Milli, UnitKind::Watt);
pub const U_UW: Unit = Unit::new(SiPrefix::Micro, UnitKind::Watt);

// Degrees
pub const U_DEGREE: Unit = Unit::new(SiPrefix::None, UnitKind::Degree);

/// Convenience: create a UnitValue from raw f64 + Unit
pub fn val(value: f64, unit: Unit) -> UnitValue {
    UnitValue::new(value, unit)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_unit_value_creation() {
        let v = UnitValue::new(1.0, U_KOHM);
        assert_eq!(v.value, 1000.0);

        let v = UnitValue::new(10.0, U_PF);
        assert_eq!(v.value, 10e-12);

        let v = UnitValue::new(3.3, U_V);
        assert_eq!(v.value, 3.3);
    }

    #[test]
    fn test_str_spice() {
        let v = UnitValue::new(1.0, U_KOHM);
        assert_eq!(v.str_spice(), "1k");

        let v = UnitValue::new(10.0, U_PF);
        assert_eq!(v.str_spice(), "10p");

        let v = UnitValue::new(100.0, U_NS);
        assert_eq!(v.str_spice(), "100n");

        let v = UnitValue::new(3.3, U_V);
        assert_eq!(v.str_spice(), "3.3");

        let v = UnitValue::new(1.0, U_UH);
        assert_eq!(v.str_spice(), "1u");
    }

    #[test]
    fn test_display() {
        let v = UnitValue::new(1.0, U_KOHM);
        assert_eq!(format!("{}", v), "1kOhm");
    }
}

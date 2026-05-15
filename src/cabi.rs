//! C ABI exports for direct linking.

use std::ffi::{CStr, CString};
use std::os::raw::c_char;

use crate::circuit::*;
use crate::unit::*;

/// Opaque circuit handle for C consumers
pub struct SCircuit {
    inner: Circuit,
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_new(title: *const c_char) -> *mut SCircuit {
    let title = unsafe { CStr::from_ptr(title) }
        .to_str()
        .unwrap_or("untitled");
    Box::into_raw(Box::new(SCircuit {
        inner: Circuit::new(title),
    }))
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_free(c: *mut SCircuit) {
    if !c.is_null() {
        drop(unsafe { Box::from_raw(c) });
    }
}

// ── Component addition ──

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_resistor(
    c: *mut SCircuit,
    name: *const c_char,
    n1: *const c_char,
    n2: *const c_char,
    value: f64,
) {
    let c = unsafe { &mut *c };
    let name = cstr_to_str(name);
    let n1 = cstr_to_str(n1);
    let n2 = cstr_to_str(n2);
    c.inner.r(name, n1, n2, value);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_capacitor(
    c: *mut SCircuit,
    name: *const c_char,
    n1: *const c_char,
    n2: *const c_char,
    value: f64,
) {
    let c = unsafe { &mut *c };
    let name = cstr_to_str(name);
    let n1 = cstr_to_str(n1);
    let n2 = cstr_to_str(n2);
    c.inner.c(name, n1, n2, value);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_inductor(
    c: *mut SCircuit,
    name: *const c_char,
    n1: *const c_char,
    n2: *const c_char,
    value: f64,
) {
    let c = unsafe { &mut *c };
    let name = cstr_to_str(name);
    let n1 = cstr_to_str(n1);
    let n2 = cstr_to_str(n2);
    c.inner.l(name, n1, n2, value);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_mosfet(
    c: *mut SCircuit,
    name: *const c_char,
    d: *const c_char,
    g: *const c_char,
    s: *const c_char,
    b: *const c_char,
    model: *const c_char,
) {
    let c = unsafe { &mut *c };
    c.inner.m(
        cstr_to_str(name),
        cstr_to_str(d),
        cstr_to_str(g),
        cstr_to_str(s),
        cstr_to_str(b),
        cstr_to_str(model),
    );
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_bjt(
    c: *mut SCircuit,
    name: *const c_char,
    nc: *const c_char,
    nb: *const c_char,
    ne: *const c_char,
    model: *const c_char,
) {
    let c = unsafe { &mut *c };
    c.inner.q(
        cstr_to_str(name),
        cstr_to_str(nc),
        cstr_to_str(nb),
        cstr_to_str(ne),
        cstr_to_str(model),
    );
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_diode(
    c: *mut SCircuit,
    name: *const c_char,
    np: *const c_char,
    nm: *const c_char,
    model: *const c_char,
) {
    let c = unsafe { &mut *c };
    c.inner.d(
        cstr_to_str(name),
        cstr_to_str(np),
        cstr_to_str(nm),
        cstr_to_str(model),
    );
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_voltage_source(
    c: *mut SCircuit,
    name: *const c_char,
    np: *const c_char,
    nm: *const c_char,
    value: f64,
) {
    let c = unsafe { &mut *c };
    c.inner
        .v(cstr_to_str(name), cstr_to_str(np), cstr_to_str(nm), value);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_current_source(
    c: *mut SCircuit,
    name: *const c_char,
    np: *const c_char,
    nm: *const c_char,
    value: f64,
) {
    let c = unsafe { &mut *c };
    c.inner
        .i(cstr_to_str(name), cstr_to_str(np), cstr_to_str(nm), value);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_add_model(
    c: *mut SCircuit,
    name: *const c_char,
    kind: *const c_char,
    params_json: *const c_char,
) {
    let c = unsafe { &mut *c };
    let name = cstr_to_str(name);
    let kind = cstr_to_str(kind);
    // params_json: "KEY1=VAL1 KEY2=VAL2" simple format
    let params_str = cstr_to_str(params_json);
    let params: Vec<Param> = params_str
        .split_whitespace()
        .filter_map(|s| {
            let (k, v) = s.split_once('=')?;
            Some(Param::new(k, v))
        })
        .collect();
    c.inner.model(name, kind, params);
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_include(c: *mut SCircuit, path: *const c_char) {
    let c = unsafe { &mut *c };
    c.inner.include(cstr_to_str(path));
}

#[unsafe(no_mangle)]
pub extern "C" fn circuit_lib(c: *mut SCircuit, path: *const c_char, section: *const c_char) {
    let c = unsafe { &mut *c };
    c.inner.lib(cstr_to_str(path), cstr_to_str(section));
}

// ── Output ──

/// Emit SPICE netlist. Caller must free with `circuit_free_string`.
#[unsafe(no_mangle)]
pub extern "C" fn circuit_to_spice(c: *const SCircuit) -> *mut c_char {
    let c = unsafe { &*c };
    let netlist = c.inner.to_string();
    CString::new(netlist).unwrap().into_raw()
}

/// Free a string returned by circuit_to_spice
#[unsafe(no_mangle)]
pub extern "C" fn circuit_free_string(s: *mut c_char) {
    if !s.is_null() {
        drop(unsafe { CString::from_raw(s) });
    }
}

// ── Helpers ──

fn cstr_to_str(ptr: *const c_char) -> &'static str {
    unsafe { CStr::from_ptr(ptr) }.to_str().unwrap_or("")
}

#!/usr/bin/env bash

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" || exit; pwd)

function print_error
{
    # shellcheck disable=SC2145
    echo -e "\033[31m$@\033[0m" 1>&2
}

function print_message
{
    # shellcheck disable=SC2145
    echo -e "\033[32m$@\033[0m"
}

function on_interrupt_trap
{
    print_error "An interrupt signal was detected."
    exit 1
}

trap on_interrupt_trap INT

ARGS=("--config-file=${ROOT_DIR}/mypy.ini")

print_message "mypy ${ARGS[*]}"

"$ROOT_DIR/python" -m mypy "${ARGS[@]}" \
    "$ROOT_DIR/mwfilter/" \
    "$ROOT_DIR/tester/" \
    "$ROOT_DIR/setup.py"

// package.sv
package my_package;

    // Оголошення типу даних
    typedef enum logic [1:0] {
        IDLE,
        RUNNING,
        STOPPED
    } state_t;

    // Оголошення константи
    localparam int MAX_COUNT = 10;

    // Оголошення функції
    function int add(int a, int b);
        return a + b;
    endfunction


endpackage

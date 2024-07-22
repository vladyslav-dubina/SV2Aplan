// package.sv
package my_package;

    typedef enum logic [1:0] {
        IDLE,
        RUNNING,
        STOPPED
    } state_t;

    localparam int MAX_COUNT = 10;

    function int add(int a, int b);
        return a + b;
    endfunction


endpackage

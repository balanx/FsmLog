
module  test (
  input                clk
, input                rst
, input             i
,output reg         y
);

reg  [7:0]  x ;
wire         f ;
assign  f = ~x ;

localparam [2:0]
S0 = 0 ,
S1 = 1 ,
S2 = 2 ,
S3 = 3 ,
S4 = 4 ,
S5 = 5 ;

reg  [2:0]  state, next_st ;

always @(posedge clk)
    if (rst)
        state <= S0 ;
    else
        state <= next_st ;


always @* begin
    next_st = state ;

    case(state)
        S0 :
            if (i==1'b1)
                next_st = S1 ;

        S1 :
            if (i==1'b1)
                next_st = S2 ;
            else if (i==1'b0)
                next_st = S3 ;

        S2 :
            if (i==1'b1)
                next_st = S0 ;
            else 
                next_st = S4 ;

        S3 :
            next_st = S1 ;

        S4 :
            if (i==1'b0)
                next_st = S5 ;
            else if (i==1'b1)
                next_st = S3 ;

        S5 :
            if (i==1'b0)
                next_st = S0 ;
            else if (i==1'b1)
                next_st = S2 ;

        default :
                next_st = S0 ;
    endcase
end

always @(posedge clk)
    if (rst) begin
        x <= 8'd0 ;
        y <= 1'd0 ;
    end
    else begin
        x <= 8'd0 ;

        if (state == S2)
            y <= 1 ;
        else if (state == S5)
            y <= 0 ;

        if (state == S1 && next_st == S2)
            x <= 1 ;
        else if (state == S4 && next_st == S3)
            x <= 2 ;

    end

endmodule // fsmlog


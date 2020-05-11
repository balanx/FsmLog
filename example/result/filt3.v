
module filt3 (
  output reg   y = 1'd0,
  input        i,

  input    clk
);


localparam
Z0 = 3'd0,
Z1 = 3'd1,
Z2 = 3'd2,
E0 = 3'd3,
E1 = 3'd4,
E2 = 3'd5;

reg [2:0] state1, next1;
always @(posedge clk)
  state1 <= next1;


always @(*) begin
  next1 = state1;

  case(state1)
    Z0 :
      if (i==1'b1)
        next1 = Z1;
    Z1 :
      if (i==1'b1)
        next1 = Z2;
      else if (i==1'b0)
        next1 = Z0;
    Z2 :
      if (i==1'b1)
        next1 = E0;
      else if (i==1'b0)
        next1 = Z0;
    E0 :
      if (i==1'b0)
        next1 = E1;
    E1 :
      if (i==1'b0)
        next1 = E2;
      else if (i==1'b1)
        next1 = E0;
    E2 :
      if (i==1'b0)
        next1 = Z0;
      else if (i==1'b1)
        next1 = E0;
    default :
        next1 = Z0;
  endcase
end

always @(posedge clk) begin
//y <= 1'd0;

  case (state1)
    Z0 : begin
        y <= 1'b0;
      end
    E0 : begin
        y <= 1'b1;
      end

  endcase
end

endmodule // @FsmLog

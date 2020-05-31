
module cnt1 (
  output     [4:0] st,
  output reg       we = 1'd0,
  output reg [4:0] addr = 5'd0,
  output reg       csn = 1'd1,
  input            req,

  input    rst,
  input    clk
);

reg [4:0] cnt = 5'd0;
reg [1:0] req_d = 2'd0;

wire  gap = (cnt>=3);
wire  len = (cnt>=19);
assign st = cnt;

localparam
IDLE = 3'd0,
CS0 = 3'd1,
DATA = 3'd2,
CS1 = 3'd3,
REDY = 3'd4;

reg [2:0] state1, next1;
always @(posedge clk or posedge rst)
if (rst)
  state1 <= IDLE;
else
  state1 <= next1;


always @(*) begin
  next1 = state1;

  case(state1)
    IDLE :
      if (req_d[1])
        next1 = CS0;
    CS0 :
      if (gap)
        next1 = DATA;
    DATA :
      if (len)
        next1 = CS1;
    CS1 :
      if (gap)
        next1 = REDY;
    REDY :
      if (!req_d[1])
        next1 = IDLE;
    default :
        next1 = IDLE;
  endcase
end

always @(posedge clk or posedge rst)
if (rst) begin
  cnt <= 5'd0;
  csn <= 1'd1;
  we <= 1'd0;
  addr <= 5'd0;
  req_d <= 2'd0;
end
else begin
  we <= 1'd0;
  req_d <= {req_d[0],req};
//following 0,1
    cnt <= 5'd0;
    csn <= 1'd1;
  //addr <= 5'd0;

    case (state1)
      CS0 : begin
        cnt <= cnt + 1'd1;
        if(gap) cnt <= 5'd0;
        csn <= 1'd0;
      end
      DATA : begin
        cnt <= cnt + 1'd1;
        if(len) cnt <= 5'd0;
        csn <= 1'd0;
        we <= 1'd1;
        addr <= cnt;
      end
      CS1 : begin
        cnt <= cnt + 1'd1;
        if(gap) cnt <= 5'd0;
      end
    endcase
end

endmodule // @FsmLog

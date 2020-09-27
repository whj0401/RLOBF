#include <idc.idc>


extern g_idcutil_logfile;

static LogInit()
{
    g_idcutil_logfile = fopen("idaout.txt", "w");
    if (g_idcutil_logfile == 0)
        return 0;
    return 1;
}

static LogWrite(format, str)
{
    if (g_idcutil_logfile != 0)
    {
        if (str != 0)
            return fprintf(g_idcutil_logfile, format, str);
        else
            return fprintf(g_idcutil_logfile, format);
    }

    return -1;
}

static LogTerm()
{
    if (g_idcutil_logfile == 0)
        return;
    fclose(g_idcutil_logfile);
    g_idcutil_logfile = 0;
}

static logtest()
{
    LogInit(); 
    LogWrite("Hello world from IDC!\n", 0);
    LogTerm();

    Exit(0);
}

static main() {

	Wait();

    auto addr, end, args, locals, frame, firstArg, name, ret;
    addr = 0;

    LogInit();

    for (addr = NextFunction(addr); addr != BADADDR; addr = NextFunction(addr)) {
        name = Name(addr);
        end = GetFunctionAttr(addr, FUNCATTR_END);
        locals = GetFunctionAttr(addr, FUNCATTR_FRSIZE);
        frame = GetFrame(addr);
        ret = GetMemberOffset(frame, " r");
        if (ret == -1) continue;
        firstArg = ret + 4;
        args = GetStrucSize(frame) - firstArg;

        dumpFunction(name, addr, end);
    }

    LogTerm();
	
	
	Exit(0);
}


static formatOperand(addr, num) {
   auto op, type, ptr, seg, var, idx, ch;
   seg = "";

   type = GetOpType(addr, num);
   op = GetOpnd(addr, num);

   if (op == "") {
      return op;
   }

   if ((ptr = strstr(op, " ptr ")) != -1) {
      op = substr(op, 0, ptr) + substr(op, ptr + 4, -1);
   }

   if ((ptr = strstr(op, "offset ")) == 0) {
      op = substr(op, ptr + 7, -1);
   }
   
   if ((ptr = strstr(op, "large ")) == 0) {
      op = substr(op, ptr + 6, -1);
   }
   
   if ((ptr = strstr(op, "ds:")) != -1) {   //drop all referencess to ds:
      op = substr(op, 0, ptr) + substr(op, ptr + 3, -1);
   }

   if ((ptr = strstr(op, ":")) != -1) {     //remember all other explicitly named segments
      seg = substr(op, ptr - 2, ptr + 1);   //keep the colon
      op = substr(op, 0, ptr - 2) + substr(op, ptr + 1, -1);
   }
   
   if (type == 2) {
      if ((ptr = strstr(op, "[")) == -1) {
         op = "[" + op + "]";
      }
   }
   else if (type == 4) {
      ptr = strstr(op, "[");
      if (ptr > 0) {
         idx = ptr - 1;
         var = "";
         while (idx >= 0) {
            ch = substr(op, idx, idx + 1);
            if (ch == " ") break;
            var = ch + var;
            idx = idx - 1;
         }
         if (var != "") {
            op = substr(op, 0, idx + 1) + "[" + var + "+" + substr(op, ptr + 1, -1);
         }
      }
   }

   if (seg != "") {
      if ((ptr = strstr(op, "[")) != -1) {
         op = substr(op, 0, ptr + 1) + seg + substr(op, ptr + 1, -1);
      }
   }
   
   return op;
}

static dumpFunction(targetname, begin, end) {
   auto addr, funcEnd, funcStart, name, line;
   auto fname, op0, op1, op0Type, op1Type, ptr;
   auto func, mnem, oper0, oper1, disp;
   auto minEA, maxEA;
   
   minEA = MinEA();
   maxEA = MaxEA();

   funcStart = begin;
   funcEnd= end;
   fname = targetname;
   
   LogWrite("USE32\n\n", 0);
   LogWrite("section .text\n\n", 0);
   LogWrite("global _%s\n\n", fname);
   LogWrite("_%s:\n", fname);
   
   for (addr = funcStart; addr != BADADDR; addr = NextHead(addr, funcEnd)) {
      if (addr != funcStart) {
         name = NameEx(addr, addr);
         if (name != "") {
            LogWrite("%s:\n", name);
         }
      }
      
      op0 = 0;
      op1 = 0;
      
      op0Type = GetOpType(addr, 0);
      op1Type = GetOpType(addr, 1);
      
      if (op0Type == 3 || op0Type == 4) {
         disp = GetOperandValue(addr, 0);
         if (disp >= minEA && disp <= maxEA) { //primarily for type 4
         }
         else {
            op0 = OpNumber(addr, 0);
         }
      }
      if (op1Type == 3 || op1Type == 4) {
         disp = GetOperandValue(addr, 1);
         if (disp >= minEA && disp <= maxEA) { //primarily for type 4
         }
         else {
            op0 = OpNumber(addr, 1);
         }
      }
            
      line = GetDisasm(addr);
      mnem = GetMnem(addr);
      oper0 = formatOperand(addr, 0);
      oper1 = formatOperand(addr, 1);

      if (mnem == "call") {
         //add leading _ in front of target function name
         //should recurs and extract this function as well
         if (op0Type >= 5 && op0Type <= 7) {  //only work with immediate offsets
            //check completed funcs list, if not found add to 
            //scheduled funcs list
            if (strstr(oper0, "_") != 0) { 
               oper0 = "_" + oper0;
            }
         }
      }
      
      if (oper0 == "" && oper1 == "") {
         if (strstr(line, mnem) != 0) {
            mnem = line;
         }
         line = form("%-8s", mnem);
      }
      else if (oper1 == "") {
         line = form("%-7s %s", mnem, oper0);
      }
      else if (oper0 == "") {
         line = form("%-7s %s", mnem, oper1);
      }
      else {
         line = form("%-7s %s, %s", mnem, oper0, oper1);
      }

      LogWrite("%d ", addr);

      LogWrite("   %s\n", line);
      if (op0) {
         OpStkvar(addr, 0);
      }
      if (op1) {
         OpStkvar(addr, 1);
      }
   }
}

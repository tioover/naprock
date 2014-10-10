use std::sync::Arc;
use std::num::abs;
use std::collections::HashMap;
use std::rand::{task_rng, Rng};
use std::comm;
use std::os;
use std::io::BufferedReader;
use std::io::File;

type M = u8;
type N = int;
type Matrix = Arc<Vec<M>>;
type Shape = (N, N);
type Value = int;
static X: N = 10;  // 矩阵行数
static Y: N = 10;  // 矩阵列数
static MAX_LOOP: uint = 100000;  // 最大循环 基本不可能达到
static TASK_NUM: uint = 1;  // 进程数，设为 1 为单进程
static BASE: uint = 4000;  // 最小循环数
static THRESHOLD: uint = 4000;  // 循环阈值


#[deriving(Clone)]
enum Step
{
    Select,
    Start,
    Left,
    Right,
    Up,
    Down,
}

#[deriving(Clone)]
struct Node
{
    matrix: Matrix,
    shape: Shape,
    center: N,
    value: Value,
    parent: Option<Arc<Node>>,
    delay: Option<(N, N)>,
    step: Step,
    depth: uint,
}


impl Node
{
    fn print(&self)
    {
        let (x, y) = self.shape;
        let matrix = self.matrix.as_slice();
        for i in range(0, x as uint) {
            let j = y as uint;
            println!("{}", matrix.slice(i*j, i*j+j));
        }
        println!("value: {} center: [{}] {} step: {}\n",
                 self.value, self.center, (self.center / y + 1, self.center % y + 1), self.depth);
    }

    fn print_step(&self)
    {
        match self.parent {
            None => (),
            Some(ref parent) => parent.print_step(),
        }
        match self.step {
            Select => println!("\nselect {}", self.center),
            Left => print!("L"),
            Right => print!("R"),
            Up => print!("U"),
            Down => print!("D"),
            Start => (),
        }
    }
    
    fn write_step(&self)
    {
        let (_, b) = self.shape;
        let mut steps = Vec::new();
        let mut now = self;
        let mut select_num = 0u;
        let mut swap_num = 0u;
        loop {
            steps.push(match now.step {
                Select => {
                    let center = now.center;
                    let pos = (center % b) * 16 + (center / b);
					let now_swap = swap_num;
                    swap_num = 0;
                    select_num += 1;
                    format!("\r\n{:02X}\r\n{}\r\n", pos, now_swap)
                },
                Left => {swap_num += 1; "L".to_string()},
                Right => {swap_num += 1; "R".to_string()},
                Up => {swap_num += 1; "U".to_string()},
                Down => {swap_num += 1; "D".to_string()},
                Start => break,
            });
			match now.parent {
			    Some(ref next) => {now = next.deref();},
				None => fail!("not break???")
			}
        }
        steps.push(format!("{}", select_num));	
        let mut file = File::create(&Path::new("solved.txt"));
		steps.reverse();
		for line in steps.iter() {
            file.write(line.as_bytes());
		}
    }
}


fn point_value(index: uint, value: u8, shape: Shape) -> int {
    let i = index as int;
    let v = value as int;
    let (_, b) = shape;
    let y = b as int;
    abs(i/y - v/y) + abs((i % y) - (v % y))
}


fn valuation(matrix: &Matrix, shape: Shape) -> Value
{
    let mut value: Value = 0;
    for i in range(0, matrix.len()) {
        value += point_value(i, *matrix.get(i), shape)
    }
    value
}


fn get_shift(step: Step, shape: Shape, center: N) -> Option<N> {
    let (x, y) = shape;
    match step {
        Up => if center >= y {Some(center - y)} else {None},
        Down => if center < x*y - y {Some(center + y)} else {None},
        Left => if center % y != 0 {Some(center - 1)} else {None},
        Right => if (center + 1) % y != 0 {Some(center + 1)} else {None},
        _ => fail!("turn arg error")
    }
}


fn local_valuation(parent: &Arc<Node>, shift: N) -> Value {
    let old_value = parent.value;
    let matrix = parent.matrix.as_slice();
    let c = parent.center as uint;
    let s = shift as uint;
    let shape = parent.shape;
    let old = point_value(c, matrix[c], shape) + point_value(s, matrix[s], shape);
    let new = point_value(s, matrix[c], shape) + point_value(c, matrix[s], shape);
    old_value - old + new
}

fn turn(parent: Arc<Node>, step: Step) -> Option<Arc<Node>>
{
    let shape = parent.shape;
    let center = parent.center;
    match get_shift(step, shape, center) {
        None => None,
        Some(shift) => {
            let node = Arc::new(
                Node {
                    value: local_valuation(&parent, shift),
                    matrix: parent.matrix.clone(),
                    shape: shape,
                    parent: Some(parent.clone()),
                    center: shift,
                    step: step,
                    depth: parent.depth + 1,
                    delay: Some((center, shift)),
                }
            );
            Some(node)
        }
    }
}


fn insert(open: &mut Vec<Arc<Node>>, node: Arc<Node>) -> ()
{
    let value = node.value;
    let len = open.len();

    if len == 0 || open.get(len-1).value >= value {
        open.push(node);
    }
    else if open.get(0).value < value {
        open.insert(0, node);
    }
    else {
        for i in range(0, len) {
            let n = len-1-i;
            if open.get(n).value >= node.value {
                open.insert(n, node);
                break;
            }
        }
    }
}

fn add(open: &mut Vec<Arc<Node>>, node: Arc<Node>) -> () {
    let mut shift = [Up, Down, Left, Right];
    task_rng().shuffle(shift);
    for step in shift.iter() {
        match turn(node.clone(), *step) {
            None => (),
            Some(new_node) => insert(open, new_node),
        };
    };
}


fn is_update(raw: &Arc<Node>, new: &Arc<Node>) -> bool {
    (new.value < raw.value) || (new.value == raw.value && new.depth < raw.depth)
}


fn force(node: Arc<Node>) -> Arc<Node>{
    match node.delay {
        None => node,
        Some((a, b)) => {
            let mut matrix = node.matrix.deref().clone();
            {
                let matrix_slice = matrix.as_mut_slice();
                matrix_slice.swap(a as uint, b as uint);
            }
            let mut node = node.deref().clone();
            node.matrix = Arc::new(matrix);
            node.delay = None;
            Arc::new(node)
        }
    }
}


fn solve_with_node(
        root: Arc<Node>,
        open: &mut Vec<Arc<Node>>,
        close: &mut HashMap<Vec<u8>, Arc<Node>>
    ) -> Arc<Node>
{
    let mut update = 0;
    let mut solution = root.clone();
    open.push(root);
    for i in range(0, MAX_LOOP) {
        if i > BASE && i - update > THRESHOLD {break;}
        match open.pop() {
            None => {println!("ERROR: Open empty."); break},
            Some(delay_node) => {
                let node = force(delay_node);
                let value = node.value;
                if value == 0 {return node;}
                match close.find(node.matrix.deref()) {
                    Some(old_node) => {
                        continue;
                    },
                    None => (),
                }
                close.insert(node.matrix.deref().clone(), node.clone());
                if is_update(&solution, &node) {
                    solution = node.clone();
                    update = i;
                };
                add(open, node);
            }
        }
    }
    solution
}

fn solve_loop(root: Arc<Node>) -> Arc<Node>
{
    let (tx, rx): (Sender<Arc<Node>>, Receiver<Arc<Node>>) = comm::channel();
    let (x, y) = root.shape;
    let len = (x*y) as uint;
    fn cmp(b: &Arc<Node>, a: &Arc<Node>) -> Ordering {
        match a.value.cmp(&b.value) {
            Equal => b.depth.cmp(&a.depth),
            x => x,
        }
    };
    for id in range(0, TASK_NUM) {
        let task_tx = tx.clone();
        let new = root.clone();
        spawn(proc() {
            let mut solutions = Vec::with_capacity(len/2);
            let mut open: Vec<Arc<Node>> = Vec::with_capacity(MAX_LOOP * 3);
            let mut close = HashMap::with_capacity(MAX_LOOP * 3);
            for i in range(0, len) {
                if i % TASK_NUM != id {continue}
                let mut now = new.deref().clone();
                now.center = i as N;
                now.parent = Some(new.clone());
                now.step = Select;
                now.depth += 1;
                solutions.push(
                    solve_with_node(
                        Arc::new(now),
                        &mut open,
                        &mut close
                    )
                );
                open.clear();
                close.clear();
            }
            solutions.sort_by(cmp);
            match solutions.pop() {
                None => fail!("error in thread return"),
                Some(solution) => task_tx.send(solution),
            }
        });
    }
    let mut pre_solutions = Vec::with_capacity(len);
    for _ in range(0, TASK_NUM) {
        pre_solutions.push(rx.recv());
    }
    pre_solutions.sort_by(cmp);
    match pre_solutions.pop() {
        Some(solution) => solution,
        _ => fail!("error in solve_loop return.")
    }
}


fn solve(matrix: Matrix, shape: Shape, select_num: uint)
{
    let mut root = Arc::new(Node {
        value: valuation(&matrix, shape),
        matrix: matrix,
        shape: shape,
        center: 0,
        depth: 0,
        step: Start,
        parent: None,
        delay: None,
    }); // init
    for i in range(0, select_num) {
        root = solve_loop(root);
        if root.value == 0 {break;}
        println!("=========={}", i);
        root.print();
    }
    println!("===");
    root.print();
    println!("write");
    root.write_step();
    println!("end");
}


fn str_int(x: &String) -> int {
    match from_str(x.as_slice().trim()) {Some(n) => n, None => fail!("args error")}
}


fn main()
{
	let args = os::args();
	let nums: Vec<int> = args.slice(1, args.len()).iter().map(str_int).collect();
	println!("{}", nums);
	let x: int = nums[0];
	let y: int = nums[1];
	let path = Path::new("marked.txt");
	let mut file = BufferedReader::new(File::open(&path));
	let lines: Vec<String> = file.lines().map(|x| x.unwrap()).collect();
	let matrix: Vec<u8> = lines.iter().map(|x| str_int(x) as u8).collect();
	println!("{}", matrix);
    solve(Arc::new(matrix), (x, y), 16);
}

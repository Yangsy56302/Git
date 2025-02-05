# Baba Make Parabox
![Baba](logo/a8icon_240x160.png)![Make](logo/a8icon_240x160.png)![Parabox](logo/a8icon_240x160.png)

**Baba Make Parabox**（简称 **BMP**）是**Yangsy56302**以推箱子游戏[**Baba Is You**（by Arvi Hempuli）](https://hempuli.com/baba/)的机制为基础进行二次创作，缝合了另一个推箱子游戏[**Patrick's Parabox**（by Patrick Traynor）](https://www.patricksparabox.com/)的主要机制而做出的推箱子游戏，目前处于开发阶段。

**本游戏的源代码使用[GNU 通用公共许可证第三版](https://www.gnu.org/licenses/gpl-3.0.html)作为开源协议。**

**本游戏使用[Pygame](https://www.pygame.org/news/)作为游戏引擎；**
**Pygame使用[GNU宽通用公共许可证 2.1版](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html)作为开源协议。**
本人不提供Pygame的源代码，而是提供使用未经修改的Pygame版本
经[PyInstaller](https://pyinstaller.org/en/stable/index.html)打包后形成的游戏程序；
**PyInstaller使用[GNU通用公共许可证 第2版](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)作为开源协议。**

**本人并未拥有游戏纹理的所有权。**
如果您有关于游戏纹理的使用权等权利的更多信息，[请尽快联系我](#联系作者)。

该游戏的雏形诞生于2024.05.15，游戏文件夹创建时间为北京时间12:12:15。

## [更新日志](changelog.md)
请去查看`changelog.md`（段落标题就是链接）。

## 新手指南
### 下载
请跳转到[Github](https://github.com/Yangsy56302/BabaMakeParabox)，
点击页面右上方写着**Code**的绿色按钮，
在展开的下拉菜单里点击最靠下的的**Download zip**即可下载所需的压缩包。

您也可以点击[此链接](https://github.com/Yangsy56302/BabaMakeParabox/archive/refs/heads/main.zip)以直接下载。

压缩包（`BabaMakeParabox-main.zip`）内含有**可执行程序（bmp.exe）**，**源代码（BabaMakeParabox/）**，
**Baba Make Parabox 添加的新纹理（sprites_new/）**， **Baba Is You 的部分音效（sounds/）** 等内容。

备用下载地址包括：
+ 需要特殊手段访问的[GitLab](https://gitlab.com/Yangsy56302/BabaMakeParabox)，
+ 前者在国内的代理[JihuLab](https://jihulab.com/BabaMakeParabox/BabaMakeParabox)，
+ 以及需要注册账号才能下载的[Gitee](https://gitee.com/Yangsy56302/BabaMakeParabox)。

### 安装
#### 推荐安装方式
1. 在您准备安装的位置（如`C:\Program Files\`）新建文件夹；
2. 将压缩包`BabaMakeParabox-main.zip`内的文件和文件夹解压到第 1 步新建的文件夹内；
3. 在第 2 步解压的文件中找到`baba-is-you-original-sprites.zip`（**Baba Is You** 的纹理），解压到与第 2 步相同的文件夹内；
4. 找到文件夹`sprites_old`，并将其重命名为`sprites`；
5. 找到文件夹`sprites_new`，并将里面的所有文件转移到在第 4 步被重命名的文件夹（`sprites`，重命名前称为`sprites_old`）里面。

#### 备用安装方式
1. 完成[推荐安装方式](#推荐安装方式)的所有步骤；
2. 通过以下任意一种方式安装**Python**：
    + 官方安装方式
        1. 进入[Python 官方网站](https://www.python.org)；
        2. 找到位于Logo右下方的**Downloads**，悬停展开；
        3. 在展开后的部分找到**Download for Windows**下方的按钮，点击以下载；
        4. 打开下载完成的安装程序，勾选最下方的**Add python.exe to PATH**，然后点击醒目的**Install Now**以安装Python；
        5. 等待安装完成，然后重启电脑。
    + _（待补）_
3. 运行`inst-win.bat`，然后耐心等待几分钟，直到文件夹内出现`bmp.exe`和`submp.exe`。

### 运行
双击运行`play-win.bat`，这将会间接运行`bmp.exe`，然后启动程序。

直接运行`bmp.exe`也是可行的，但程序崩溃时终端窗口会直接关闭，
很难看到错误信息，也就无法在汇报漏洞时完整地描述情况，所以不推荐。

如果您的**Windows**系统安装了**Python**，或者您使用了备用方式来安装游戏，
那么还可以尝试运行`run-win.bat`来启动游戏。

**游戏仅在命令行窗口存在且未选中内部文本时正常运行。**

游戏未响应时，请先在命令行内 **取消选中文字** ，
确保游戏 **并未询问输入** ，
然后耐心 **等待十秒左右** 直至游戏继续运行。

如果游戏仍然处于未响应状态或在一段时间后崩溃，则可以确认该现象是一个游戏漏洞。

## 游戏内容
**Baba Make Parabox**目前仍然处于开发阶段，游戏内容随时可能变更，因此暂未制作大型关卡包。

~~早期版本遗留的测试用关卡包文件仍能使用~~
~~（其中包括一个由[彩虹箱RainbowBox](https://space.bilibili.com/1281976796/)所制作的[玩法测试关卡包](levelpacks/mikan.4.02.json)）。~~

从[`v4.1`](changelog.md#41)起，该版本之前创建的所有的关卡包文件都将无法读取，直到游戏内置的关卡包更新系统兼容这些格式。

迫切于体验新版本更新内容的玩家可以[**自行制作关卡包**](#编辑器)。

### 游戏设定
#### 文本（`TEXT`）
**Baba Is You**中用于组成游戏规则的物体。

[文本默认可以被推动](#默认规则)，
这也是**Baba Is You**的核心内容：
自行更改可用的游戏规则以达成目标。

##### 名词
在规则内代表某种物体。

例如，`ROCK`代表场景中的岩石（Rock）。

###### 特殊名词列表
| 显示名      | ID              | 备注 |
| :---------- | :-------------- | :--- |
| **ALL**     | `text_all`      | 指代已出现的所有物体 |
| **TEXT**    | `text_text`     | 指代所有[文本](#文本text)，包括但不限于自身 |
| **SPACE**   | `text_space`    | 指代[空间](#空间space) |
| **CLONE**   | `text_clone`    | 指代[克隆空间](#克隆clone) |
| **Ø**       | `text_parabox`  | 指代悖论空间 |
| **∞**       | `text_infinity` | 指代无穷大悖论空间 |
| **ε**       | `text_epsilon`  | 指代无穷小悖论空间 |
| **LEVEL**   | `text_level`    | 指代[关卡](#关卡level) |
| **PATH**    | `text_path`     | 指代[路径](#路径path) |

###### 元文本
一种特殊的名词，用于指代某类具体的文本物体，当然也包括其他元文本。

**Baba Make Parabox**中元文本的外观与**Baba Is You**中普遍使用的外观（添加外轮廓线）不同，
而是在原本的文本基础上添加半透明数字，以代表额外的指代层数（也就是额外的`text_`数量）。

##### 属性词
在规则内代表某种性质。

例如，`PUSH`代表可以被推动（Push）的性质。
某些情况下，名词也可以作为属性词使用。

###### 新属性词列表
| 显示名      | ID（省略前缀）   | 备注 |
| :---------- | :-------------- | :--- |
| **ENTER**   | `enter`         | 物体可以进入空间；空间允许物体进入 |
| **LEAVE**   | `leave`         | 物体可以离开空间；空间允许物体离开 |
| **FLIP**    | `flip`          | 横向翻转 |
| **TEXT+**   | `text_plus`     | 元文本：物体转名词 |
| **TEXT-**   | `text_minus`    | 元文本：名词转物体 |

##### 动词
在规则内用于决定施加属性的方式（说实话这个不怎么直观）。

例如，动词`IS`会直接将后文中的性质施加给前文中的物体，
所以`ROCK IS PUSH`会将`PUSH`代表的性质施加给`ROCK`代表的物体，
最终才导致岩石能被推动。

##### 修饰词
可以限定名词的指代范围。

###### 前缀修饰词
需要放在名词之前。

例如，`SELDOM KEKE`限定了`KEKE`的范围，
其中`SELDOM`是前缀，
`KEKE`是名词。

###### 中缀修饰词~~（其实更像是后缀修饰词，之后再改吧）~~
需要放在名词之后，且需要尾随属性词以进一步确定指代范围。

例如，`BOX ON TILE`限定了`BOX`的范围，
其中`ON`是中缀，
`BOX`是名词，
而`TILE`原本是名词，在此处则用作属性词确定范围。

##### `AND`
用于并列绝大多数同类词，不支持动词。

例如，`PLANET AND ROBOT IS YOU AND ME`。

##### `NOT`
用于对词义取反，作用在名词与修饰词上时反转指代范围，
作用在属性词上时则取消物体的相同属性，不支持动词。

例如，`IT IS NOT CRAB`内的`NOT`否定`CRAB`。

##### 默认规则
可能并不是最新版。

+ `TEXT IS PUSH`
+ `CURSOR IS SELECT`
+ `NOT META LEVEL IS STOP`
+ `NOT META SPACE IS PUSH`
+ `NOT META CLONE IS PUSH`
+ `META CLONE IS NOT LEAVE`

#### 空间（`SPACE`）
容纳物体的空间。~~废话……~~

同时可以以物体的形式“出现”在空间内，甚至可以“容纳”自身，
这也是**Patrick's Parabox**的核心内容：套娃。

[空间物体默认可以被推动。](#默认规则)

##### 克隆（`CLONE`）
克隆物体是空间物体的一种变体。

克隆只允许物体进入而不允许物体离开，
这样可以避免物体可以在退出多个空间时复制自身，
尽管使用多个普通的空间物体仍然可以做到这一点。

#### 关卡（`LEVEL`）
你知道的，咱们总得有种可以将不同的关卡放在同一位置的方法吧。

多个关卡可以“引用”同一个空间（类似于多个空间物体“引用”同一个空间）。

[关卡物体默认阻挡物体通过。](#默认规则)

##### 光标（`CURSOR`）
[光标物体默认拥有`SELECT`属性](#默认规则)，
不过除此之外就真的没什么特别的了——
那些特殊功能都是`SELECT`属性所导致的。

##### 路径（`PATH`）
只有已解锁的路径物体和关卡物体才会允许带有`SELECT`特性的物体移动。
同时，路径物体的解锁条件可以在编辑器内自定义。

##### 收集物（`COLLECT`）
用于解锁路径物体。

#### 转变（Transform）
将名词用做属性可以使被作用的物体变成用作属性的物体~~这句真绕~~。

#### 特殊转变规则
+ 将空间或关卡转变为常规物体时，会保留原本的指代信息。
+ 将常规物体转变为空间或关卡时，新的物体不会指代任何空间或关卡。
    + 例外：如果原本的物体由于某些原因还保留有相关信息，则该指代信息会被新的物体使用。
+ 将空间转变为关卡时，会创建一个只引用原空间的新关卡，作为新的关卡物体所指代的关卡。
+ 将关卡转变为空间时，原关卡所引用的全部空间都会成为新的空间物体。

### 控制
+ **(`W` / `S` / `A` / `D`) / 方向键**：移动拥有`YOU`属性的物体
+ **`SPACE` / `RETURN`**：等待一轮
+ **`Z`**：撤销操作
+ **`R`**：重新开始该关卡
    + **`CTRL` + `...`**：重新开始整个关卡包
+ **`ESC`**：保存当前关卡进度，并回到上层关卡
+ **`O` / `P`**：载入 / 保存临时存档
    + **`CTRL` + `...`**：可指定此临时存档的名字 **\***
    + **`ALT` + `...`**：指定使用关卡包文件
+ **`TAB`**：显示各种信息
+ **`F1`**: 显示FPS
+ **`F12`**: 切换调试模式
+ **鼠标左键**：进入空间
+ **鼠标右键**：回到上层空间
+ **鼠标中键**：显示所选物体的信息
+ **鼠标滚轮**：循环选择空间
+ **关闭游戏窗口**：停止游玩并保存该关卡包 **\***
+ **关闭终端**：强制退出程序

## 编辑器
该章节暂不提供有关如何设计谜题等问题的信息。

### 控制
+ **鼠标左键**：放置物体
    + **`SHIFT` + `...`**：即使该位置存在物体也额外放置
    + **`CTRL` + `...`**：设置部分物体的额外信息 **\***
    + **`ALT` + `...`**：进入空间
        + **`SHIFT` + `...`**：进入关卡
+ **鼠标右键**：删除物体
    + **`ALT` + `...`**：回到上层空间
        + **`SHIFT` + `...`**：回到上层关卡
+ **鼠标中键**：从光标位置选择物体类型
+ **鼠标滚轮**：循环选择物体类型
    + **`SHIFT` + 鼠标滚轮向上滚动**：选择该物体的名词
    + **`SHIFT` + 鼠标滚轮向下滚动**：选择该名词指向的物体
    + **`ALT` + `...`**：循环选择空间
        + **`SHIFT` + `...`**：循环选择关卡
+ **(`W` / `S` / `A` / `D`) / 方向键**：选择物体朝向
+ **`0` ~ `9`**：从快捷栏选择物体类型
    + **`SHIFT` + `...`**：设置快捷栏的物体类型
+ **`N`**：新建空间 **\***
    + **`ALT` + `...`**：新建关卡 **\***
+ **`M`**：删除空间 **\***
    + **`ALT` + `...`**：删除关卡 **\***
+ **`R`**：设置全局规则 **\***
    + **`SHIFT` + `...`**：删除全局规则 **\***
+ **`T`**：设置所处空间的ID **\***
    + **`ALT` + `...`**：设置所处关卡的ID **\***
+ **`CTRL` + (`X` / `C` / `V`)**：剪切 / 复制 / 粘贴 光标上的物体
+ **`F1`**: 显示FPS
+ **`F12`**: 切换调试模式
+ **关闭游戏窗口**：停止关卡包编辑器并保存该关卡包 **\***
+ **关闭终端**：强制退出程序

**注意：带有 \* 的键位提示代表按下该键之后需要在终端内输入更多信息。**
此时游戏窗口会停止响应，信息输入完成后会恢复。

**放置的空间、克隆和关卡默认指向摄像头所在的空间和关卡。**

## 杂项
### 计划实现
+ **就在下期**
    + ~~优化关卡包存储格式。~~
        + [`v4.1`](changelog.md#41)已实现。
    + ~~收藏品改为一般物体而非独立类型。~~
        + [`v4.02`](changelog.md#402)已实现。
    + 优化关卡游玩流程，或许会参考 Maxwell's Puzzling Demon 的部分机制。
        + [`v4.1`](changelog.md#41)部分实现。
+ **短期**
    + ~~文本可以跨空间组成规则。~~
        + 难以决定规则应该在哪些空间内生效，故废除。
    + `MORE`，`YOU2`等相对容易实现的属性。
    + 纯装饰属性，如`RED`、`BLUE`等颜色。
    + GUI（图形用户界面）：
        + 在编辑器内显示更多信息，比如物体名称。
            + [`v4.03`](changelog.md#403)部分实现。
+ **中期**
    + 实现`GROUP`的逻辑。
    + 更改`ENTER`和`LEAVE`的工作方式。
        + 对于物体：
            + `ENTER`使该物体在与空间物体重合时，转移至对应空间的正中心；
            + `LEAVE`使该物体立即离开其所在的空间，转移至外层空间内与原空间物体相同的位置。
                + 由于规则不会在上层空间生效，一般情况下可以保证该物体只会离开一层空间。
        + 对于空间：
            + `ENTER`使该空间允许物体进入，`LEAVE`使该空间允许物体退出。
        + 对于关卡：
            + `ENTER`使该关卡允许物体“进入”，`LEAVE`使该关卡允许物体“退出”。
                + 判断物体是否即将“进入”或“退出”的条件类似于“对于物体”所描述的条件。
                + 物体“进入”时的位置取决于含有`YOU`属性的物体，并且允许复制。
                + 物体“退出”时的位置与“对于物体”所描述的位置相同。
+ **长期**
    + 重新加入平滑移动插值。
        + 一个或许更简单的实现方式：记录所有物体在上一轮的显示位置，而不是物理位置。
            + 这样或许也可以实现使物体出现或消失时通过改变其透明度进行提示。
    + GUI（图形用户界面）：
        + 使用可输入文本的游戏窗口取代命令行的显示。
    + _`GAME`的复杂语法。_
        + 目前对`GAME`应用修饰词会使其不指代任何物体。
    + `Too Complex`。
    + `Infinite Loop`与其检测方法。
+ **遥遥无期**
    + _官方关卡包……？_

### 异常情况分类
#### 游戏特性
+ ~~属性前带有多个`NOT`的规则只会否定一条恰好缺少一个`NOT`的规则。~~
    + [`v4.104`](changelog.md#4104)已废弃该设定。
+ `FEELING`每轮只检测一次，以试图避免检测停机问题和`Infinite Loop`。
+ `WORD`属性对`TEXT`有效。

#### 被搁置修复的游戏漏洞
+ 游戏过程中，即使镜头所在空间的方向更改，鼠标仍会使用默认方向。
+ 移动系统的完成度很低，有时表现会与预期不同，主要出现在多个物体同时移动的情况下。
    + 例如，多个常规空间物体同时存在时，物体进入该空间所复制出的新物体的数量。

## 联系作者
Bilibili：**<https://space.bilibili.com/430612354>**

QQ：**2485385799**

邮箱：**<yangsy56302@163.com>**
from html import parser
import json
import tkinter as tk
import multiprocessing
from tkinter import scrolledtext

from cobotta_control.cobotta_pro_mqtt_control import ProcessManager
from cobotta_control.tools import tool_infos


tool_ids = [tool_info["id"] for tool_info in tool_infos]


class ToolChangePopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        # 親ウインドウの手前に表示
        self.transient(parent)
        # すべてのイベントをポップアップで捕捉
        self.grab_set()
        self.title("Tool Change")
        # ポップアップを閉じるときの処理を上書き
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        tk.Label(self, text="Select a tool:").pack(pady=10)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        names = [f"Tool {i}" for i in tool_ids] + ["Cancel"]
        for name in names:
            b = tk.Button(btn_frame, text=name, width=10,
                          command=lambda n=name: self.button_pressed(n))
            b.pack(side=tk.LEFT, padx=5)

        # ポップアップが閉じるまで待機    
        self.wait_window()
    
    def button_pressed(self, name):
        if name == "Cancel":
            self.result = None
        else:
            self.result = int(name.split(" ")[1])
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()


class MQTTWin:
    def __init__(self, root):
        self.pm = ProcessManager()
        print("Starting Process!")
        self.pm.startDebug()
 
        self.root = root
        self.root.title("MQTT-CobottaPro900 Controller")
        self.root.geometry("700x900")

        for col in range(4):
            self.root.grid_columnconfigure(col, weight=1, uniform="equal")
        
        self.button_ConnectRobot = \
            tk.Button(self.root, text="ConnectRobot", padx=5,
                      command=self.ConnectRobot, state="normal")
        self.button_ConnectRobot.grid(row=0,column=0,padx=2,pady=2,sticky="ew")

        self.button_ConnectMQTT = \
            tk.Button(self.root, text="ConnectMQTT", padx=5,
                             command=self.ConnectMQTT, state="normal")
        self.button_ConnectMQTT.grid(row=0,column=1,padx=2,pady=2,sticky="ew")

        self.button_EnableRobot = \
            tk.Button(self.root, text="EnableRobot", padx=5,
                      command=self.EnableRobot, state="disabled")
        self.button_EnableRobot.grid(row=1,column=0,padx=2,pady=2,sticky="ew")

        self.button_DisableRobot = \
            tk.Button(self.root, text="DisableRobot", padx=5,
                      command=self.DisableRobot, state="disabled")
        self.button_DisableRobot.grid(row=1,column=1,padx=2,pady=2,sticky="ew")

        self.button_ReleaseHand = \
            tk.Button(self.root, text="ReleaseHand", padx=5,
                      command=self.ReleaseHand, state="disabled")
        self.button_ReleaseHand.grid(row=1,column=2,padx=2,pady=2,sticky="ew")

        self.button_DefaultPose = \
            tk.Button(self.root, text="DefaultPose", padx=5,
                      command=self.DefaultPose, state="disabled")
        self.button_DefaultPose.grid(row=2,column=0,padx=2,pady=2,sticky="ew")

        self.button_TidyPose = \
            tk.Button(self.root, text="TidyPose", padx=5,
                      command=self.TidyPose, state="disabled")
        self.button_TidyPose.grid(row=2,column=1,padx=2,pady=2,sticky="ew")

        self.button_ClearError = \
            tk.Button(self.root, text="ClearError", padx=5,
                      command=self.ClearError, state="disabled")
        self.button_ClearError.grid(row=2,column=2,padx=2,pady=2,sticky="ew")

        self.button_StartMQTTControl = \
            tk.Button(self.root, text="StartMQTTControl", padx=5,
                      command=self.StartMQTTControl, state="disabled")
        self.button_StartMQTTControl.grid(
            row=3,column=0,padx=2,pady=2,sticky="ew")
        
        self.button_StopMQTTControl = \
            tk.Button(self.root, text="StopMQTTControl", padx=5,
                      command=self.StopMQTTControl, state="disabled")
        self.button_StopMQTTControl.grid(
            row=3,column=1,padx=2,pady=2,sticky="ew")

        self.button_ToolChange = \
            tk.Button(self.root, text="ToolChange", padx=5,
                      command=self.ToolChange, state="disabled")
        self.button_ToolChange.grid(
            row=3,column=2,padx=2,pady=2,sticky="ew")

        self.frame_enabled = tk.Frame(self.root)
        self.frame_enabled.grid(row=1,column=3,padx=2,pady=2,sticky="w")
        self.canvas_enabled = \
            tk.Canvas(self.frame_enabled, width=10, height=10)
        self.canvas_enabled.pack(side="left",padx=10)
        self.light_enabled = \
            self.canvas_enabled.create_oval(1, 1, 9, 9, fill="gray")
        self.label_enabled = \
            tk.Label(self.frame_enabled, text="Enabled")
        self.label_enabled.pack(side="left",padx=2)

        self.frame_error = tk.Frame(self.root)
        self.frame_error.grid(row=2,column=3,padx=2,pady=2,sticky="w")
        self.canvas_error = \
            tk.Canvas(self.frame_error, width=10, height=10)
        self.canvas_error.pack(side="left",padx=10)
        self.light_error = \
            self.canvas_error.create_oval(1, 1, 9, 9, fill="gray")
        self.label_error = \
            tk.Label(self.frame_error, text="Error")
        self.label_error.pack(side="left",padx=2)

        self.frame_mqtt_control = tk.Frame(self.root)
        self.frame_mqtt_control.grid(row=3,column=3,padx=2,pady=2,sticky="w")
        self.canvas_mqtt_control = \
            tk.Canvas(self.frame_mqtt_control, width=10, height=10)
        self.canvas_mqtt_control.pack(side="left",padx=10)
        self.light_mqtt_control = \
            self.canvas_mqtt_control.create_oval(1, 1, 9, 9, fill="gray")
        self.label_mqtt_control = \
            tk.Label(self.frame_mqtt_control, text="MQTTControl")
        self.label_mqtt_control.pack(side="left",padx=2)

        tk.Label(self.root, text="State").grid(
            row=4, column=0, padx=2, pady=10, sticky="w", columnspan=2)
        self.string_var_states = {}
        for i in range(6):
            frame_state = tk.Frame(self.root)
            frame_state.grid(row=5+i, column=0, padx=2, pady=2, sticky="ew")
            label_target = tk.Label(frame_state, text=f"J{i + 1}")
            label_target.pack(side="left", padx=10)
            string_var_state = tk.StringVar()
            string_var_state.set("")
            self.string_var_states[f"J{i + 1}"] = string_var_state
            text_box_state = tk.Label(
                frame_state,
                textvariable=string_var_state,
                bg="white",
                relief="solid",
                bd=1,
                anchor="e",
            )
            text_box_state.pack(side="right", padx=2, expand=True, fill="x")

        frame_state = tk.Frame(self.root)
        frame_state.grid(row=5, column=1, padx=2, pady=2, sticky="ew")
        label_target = tk.Label(frame_state, text="Tool ID")
        label_target.pack(side="left", padx=10)
        string_var_state = tk.StringVar()
        string_var_state.set("")
        self.string_var_states["Tool ID"] = string_var_state
        text_box_state = tk.Label(
            frame_state,
            textvariable=string_var_state,
            bg="white",
            relief="solid",
            bd=1,
            anchor="e",
        )
        text_box_state.pack(side="right", padx=2, expand=True, fill="x")
    
        tk.Label(self.root, text="Target").grid(
            row=4, column=2, padx=2, pady=2, sticky="w", columnspan=2)
        self.string_var_targets = {}
        for i in range(6):
            frame_target = tk.Frame(self.root)
            frame_target.grid(
                row=5+i, column=2, padx=2, pady=2, sticky="ew")
            label_target = tk.Label(frame_target, text=f"J{i + 1}")
            label_target.pack(side="left", padx=10)
            string_var_target = tk.StringVar()
            string_var_target.set("")
            self.string_var_targets[f"J{i + 1}"] = string_var_target
            text_box_target = tk.Label(
                frame_target,
                textvariable=string_var_target,
                bg="white",
                relief="solid",
                bd=1,
                anchor="e",
            )
            text_box_target.pack(side="right", padx=2, expand=True, fill="x")

        frame_target = tk.Frame(self.root)
        frame_target.grid(row=5, column=3, padx=2, pady=2, sticky="ew")
        label_target = tk.Label(frame_target, text="grip")
        label_target.pack(side="left", padx=10)
        string_var_target = tk.StringVar()
        string_var_target.set("")
        self.string_var_targets["grip"] = string_var_target
        text_box_target = tk.Label(
            frame_target,
            textvariable=string_var_target,
            bg="white",
            relief="solid",
            bd=1,
            anchor="e",
        )
        text_box_target.pack(side="right", padx=2, expand=True, fill="x")

        tk.Label(self.root, text="Topics").grid(
            row=11, column=0, padx=2, pady=10, sticky="w", columnspan=4)
        topic_types = [
            "mgr/register",
            "dev",
            "robot",
            "control",
        ]
        self.string_var_topics = {
            topic: tk.StringVar() for topic in topic_types}
        self.topic_monitors = {}
        for i, topic_type in enumerate(topic_types):
            frame_topic = tk.Frame(self.root)
            frame_topic.grid(
                row=12+3*i, column=0, padx=2, pady=2,
                sticky="ew", columnspan=4)
            label_topic_type = tk.Label(frame_topic, text=topic_type)
            label_topic_type.pack(side="left", padx=2)
            label_actual_topic = tk.Label(
                frame_topic, text="(Actual Topic)")
            label_actual_topic.pack(side="left", padx=2)
            string_var_topic = self.string_var_topics[topic_type]
            text_box_topic = tk.Label(
                frame_topic,
                textvariable=string_var_topic,
                bg="white",
                relief="solid",
                bd=1,
                anchor="w",
            )
            text_box_topic.pack(side="left", padx=2, expand=True, fill="x")
            frame_topic = tk.Frame(self.root)
            frame_topic.grid(
                row=13+3*i, column=0, padx=2, pady=2,
                sticky="ew", columnspan=4, rowspan=2)
            self.topic_monitors[topic_type] = scrolledtext.ScrolledText(
                frame_topic, height=2)
            self.topic_monitors[topic_type].pack(
                side="left", padx=2, expand=True, fill="both")

        tk.Label(self.root, text="Log Monitor").grid(
            row=24, column=0, padx=2, pady=2, sticky="w", columnspan=4)
        self.log_monitor = scrolledtext.ScrolledText(
            self.root, height=10)
        self.log_monitor.grid(
            row=25,column=0,padx=2,pady=2,columnspan=4, sticky="nsew")
        self.update_monitor()

    def ConnectRobot(self):
        if self.pm.state_control and self.pm.state_monitor:
            return
        self.pm.startControl()
        self.pm.startMonitor()
        self.button_ConnectRobot.config(state="disabled")
        self.button_ClearError.config(state="normal")
        self.button_DefaultPose.config(state="normal")
        self.button_DisableRobot.config(state="normal")
        self.button_EnableRobot.config(state="normal")
        self.button_ReleaseHand.config(state="normal")
        self.button_TidyPose.config(state="normal")
        self.button_ToolChange.config(state="normal")
        if self.pm.state_recv_mqtt:
            self.button_StartMQTTControl.config(state="normal")
            self.button_StopMQTTControl.config(state="normal")

    def ConnectMQTT(self):
        if self.pm.state_recv_mqtt:
            return
        self.pm.startRecvMQTT()
        self.button_ConnectMQTT.config(state="disabled")
        self.button_ClearError.config(state="normal")
        self.button_DefaultPose.config(state="normal")
        self.button_DisableRobot.config(state="normal")
        self.button_EnableRobot.config(state="normal")
        self.button_ReleaseHand.config(state="normal")
        self.button_TidyPose.config(state="normal")
        if self.pm.state_control and self.pm.state_monitor:
            self.button_StartMQTTControl.config(state="normal")
            self.button_StopMQTTControl.config(state="normal")

    def EnableRobot(self):
        if not self.pm.state_control:
            return
        self.pm.enable()

    def DisableRobot(self):
        if not self.pm.state_control:
            return
        self.pm.disable()

    def DefaultPose(self):
        if not self.pm.state_control:
            return
        self.pm.default_pose()
    
    def TidyPose(self):
        if not self.pm.state_control:
            return
        self.pm.tidy_pose()

    def ClearError(self):
        if not self.pm.state_control:
            return
        self.pm.clear_error()

    def StartMQTTControl(self):
        if ((not self.pm.state_control) or
            (not self.pm.state_monitor) or
            (not self.pm.state_recv_mqtt)):
            return
        self.pm.start_mqtt_control()

    def StopMQTTControl(self):
        if ((not self.pm.state_control) or
            (not self.pm.state_monitor) or
            (not self.pm.state_recv_mqtt)):
            return
        self.pm.stop_mqtt_control()

    def ReleaseHand(self):
        if not self.pm.state_control:
            return
        self.pm.release_hand()

    def ToolChange(self):
        if not self.pm.state_control:
            return
        popup = ToolChangePopup(self.root)
        tool_id = popup.result
        if tool_id is None:
            return
        self.pm.tool_change(tool_id)

    def update_monitor(self):
        # モニタープロセスからの情報
        log = self.pm.get_current_monitor_log()
        all_log_str = ""
        if log:
            # ロボットの姿勢情報が流れるトピック
            topic_type = log.pop("topic_type")
            topic = log.pop("topic")
            log_str = json.dumps(log, ensure_ascii=False)
            self.string_var_topics[topic_type].set(topic)
            self.topic_monitors[topic_type].delete("1.0", tk.END)
            self.topic_monitors[topic_type].insert(tk.END, log_str + "\n")
            self.log_monitor.delete("1.0", tk.END)
            self.log_monitor.insert(tk.END, log_str + "\n")  # ログを表示

            # 各情報をパース
            color = "lime" if log.get("enabled") else "gray"
            self.canvas_enabled.itemconfig(self.light_enabled, fill=color)
            color = "lime" if log.get("mqtt_control") == "ON" else "gray"
            self.canvas_mqtt_control.itemconfig(
                self.light_mqtt_control, fill=color)
            color = "red" if "error" in log else "gray"
            self.canvas_error.itemconfig(self.light_error, fill=color)
            joints = log.get("joints")
            if joints is not None:
                for i in range(6):
                    self.string_var_states[f"J{i + 1}"].set(f"{joints[i]:.2f}")
            else:
                for i in range(6):
                    self.string_var_states[f"J{i + 1}"].set("")
            tool_id = log.get("tool_id")
            if tool_id is not None:
                self.string_var_states["Tool ID"].set(f"{tool_id}")
            else:
                self.string_var_states["Tool ID"].set("")

            all_log_str += log_str + "\n"

        # MQTT制御プロセスからの情報
        log = self.pm.get_current_mqtt_control_log()
        if log:
            topic_type = log.pop("topic_type")
            topic = log.pop("topic")
            log_str = json.dumps(log, ensure_ascii=False)
            self.string_var_topics[topic_type].set(topic)
            self.topic_monitors[topic_type].delete("1.0", tk.END)
            self.topic_monitors[topic_type].insert(tk.END, log_str + "\n")

            joints = log.get("joints")
            if joints is not None:
                for i in range(6):
                    self.string_var_targets[f"J{i + 1}"].set(f"{joints[i]:.2f}")
            else:
                for i in range(6):
                    self.string_var_targets[f"J{i + 1}"].set("")
            grip = log.get("grip")
            if grip is not None:
                self.string_var_targets["grip"].set(f"{grip}")
            else:
                self.string_var_targets["grip"].set("")

            all_log_str += log_str + "\n"

        trim_logs = False
        # 古いログを全て削除
        if not trim_logs:
            self.log_monitor.delete("1.0", tk.END)
        self.log_monitor.insert(tk.END, all_log_str + "\n")  # ログを表示
        if trim_logs:
            # 古いログを一部削除
            self.trim_logs(self.log_monitor, max_lines=100)
            self.log_monitor.see(tk.END)  # 最新ログにスクロール
        self.root.after(100, self.update_monitor)  # 100ms間隔で表示を更新

    def trim_logs(self, log, max_lines: int) -> None:
        """最大行数を超えたログを削除。"""
        current_lines = int(log.index('end-1c').split('.')[0])  # 現在の行数を取得
        if current_lines > max_lines:
            excess_lines = current_lines - max_lines
            self.log_area.delete("1.0", f"{excess_lines}.0")  # 超過分の行を削除


if __name__ == '__main__':
    print("Freeze Support for Windows")
    multiprocessing.freeze_support()


    # NOTE: 現在ロボットに付いているツールが何かを管理する方法がないので
    # ロボット制御コードの使用者に指定してもらう
    # ツールによっては、ツールとの通信が不要なものがあるので、通信の成否では判定できない
    # 現在のツールの状態を常にファイルに保存しておき、ロボット制御コードを再起動するときに
    # そのファイルを読み込むようにすれば管理はできるが、エラーで終了したときに
    # ファイルの情報が正確かいまのところ保証できないので、指定してもらう
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tool-id",
        type=int,
        required=True,
        choices=tool_ids,
        help="現在ロボットに付いているツールのID",
    )
    args = parser.parse_args()
    import os
    # HACK: コードの変化を少なくするため、
    # ロボット制御プロセスに引数で渡すのではなく環境変数で渡す
    os.environ["TOOL_ID"] = str(args.tool_id)

    root = tk.Tk()
    mqwin = MQTTWin(root)
    mqwin.root.lift()
    root.mainloop()

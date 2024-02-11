
(cl:in-package :asdf)

(defsystem "yolo_ros-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :std_msgs-msg
)
  :components ((:file "_package")
    (:file "BoxArray" :depends-on ("_package_BoxArray"))
    (:file "_package_BoxArray" :depends-on ("_package"))
  ))
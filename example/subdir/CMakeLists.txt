add_custom_target(${dir}_wait
  COMMAND ${CMAKE_COMMAND} -E sleep 0.${wait_time}
)
add_test(${dir}_test
  ${CMAKE_COMMAND} -E sleep 0.${wait_time}
)
install(CODE
  "execute_process(COMMAND \${CMAKE_COMMAND} -E sleep 0.${wait_time})"
)
